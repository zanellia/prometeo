"""Matrix expressions: NumPy-like syntax for linear algebra, lowered to calls
of BLASFEO-based routines.

    P = Q + A.T @ P_next @ A - K.T @ R @ K
    L = cholesky(M)
    X = -cho_solve(L, B)

The checker builds, for every assignment of a matrix expression, a tree of
the classes below with the shapes of all subexpressions. Before a program is
run (Python) or transpiled (C), lower() replaces each of these assignments
with a sequence of calls that write the result into the target matrix:

- C = s * A @ B + t * C2 ... is computed term by term into C: the first term
  initializes C (copy, transpose, or C = 0 followed by a product), the others
  are accumulated (pmt_gead, pmt_gemm_ab_xy with beta = 1);
- transposes are pushed down to the operands, A.T @ B uses gemm_tn;
- operands of products that are not (transposed) matrices, e.g. the product
  A.T @ P in A.T @ P @ A, are computed into temporaries, which are declared
  at the beginning of the function with sizes known at compile time;
- if the target matrix is read by the expression (other than as a term
  C + ...), the result is computed into a temporary and then copied;
- scalar factors other than literals and variables are computed first, into
  scalar temporaries, so that they read the data before it is overwritten.

Python and C run the same lowered code, so they give identical results.
"""

import ast
from copy import deepcopy

from .normalize import eval_dims


class LoweringError(Exception):
    def __init__(self, node, message):
        super().__init__(message)
        self.node = node
        self.message = message


class Dim:
    """A matrix dimension: its value (None if unknown at compile time) and an
    expression for it (dims constants and literals), to declare temporaries."""

    def __init__(self, value, node=None):
        self.value = value
        self.node = node

    def expr(self):
        if self.node is not None:
            return deepcopy(self.node)
        return ast.Constant(self.value)

    def __eq__(self, other):
        return self.value is not None and self.value == other.value

    def __str__(self):
        if self.value is None:
            return '?'
        return str(self.value)


UNKNOWN = Dim(None)


class MExpr:
    shape = (UNKNOWN, UNKNOWN)


class Leaf(MExpr):
    """A matrix (a variable, an attribute or an element of a List) or a block
    of one, A[a:b, c:d] (node is then the Subscript)."""

    def __init__(self, node, shape, trans=False):
        self.node = node
        self.shape = shape
        self.trans = trans

    def transposed(self):
        return Leaf(self.node, (self.shape[1], self.shape[0]), not self.trans)


class Scale(MExpr):
    def __init__(self, coef, expr):
        self.coef = coef
        self.expr = expr
        self.shape = expr.shape


class Add(MExpr):
    def __init__(self, left, right, sign=1.0):
        self.left = left
        self.right = right
        self.sign = sign
        self.shape = left.shape


class MatMul(MExpr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.shape = (left.shape[0], right.shape[1])


class Transpose(MExpr):
    def __init__(self, expr):
        self.expr = expr
        self.shape = (expr.shape[1], expr.shape[0])


class Call(MExpr):
    """cholesky(M), cho_solve(L, B)."""

    def __init__(self, name, args, shape, node):
        self.name = name
        self.args = args
        self.shape = shape
        self.node = node


# functions on matrices that can be used in matrix expressions -> arity
MATRIX_FUNCTIONS = {'cholesky': 1, 'cho_solve': 2}


class Coef:
    """A scalar factor: a constant times a product of scalar expressions."""

    def __init__(self, const=1.0, factors=()):
        self.const = const
        self.factors = list(factors)

    def __mul__(self, other):
        return Coef(self.const * other.const, self.factors + other.factors)

    def is_one(self):
        return self.const == 1.0 and not self.factors


ONE = Coef()


def leaves(e):
    if isinstance(e, Leaf):
        return [e]
    if isinstance(e, Scale):
        return leaves(e.expr)
    if isinstance(e, Transpose):
        return leaves(e.expr)
    if isinstance(e, (Add, MatMul)):
        return leaves(e.left) + leaves(e.right)
    if isinstance(e, Call):
        return [l for a in e.args for l in leaves(a)]
    raise TypeError(e)


def push_transposes(e, trans=False):
    """Move transposes down to the leaves: (A @ B).T = B.T @ A.T."""
    if isinstance(e, Leaf):
        return e.transposed() if trans else e
    if isinstance(e, Transpose):
        return push_transposes(e.expr, not trans)
    if isinstance(e, Scale):
        return Scale(e.coef, push_transposes(e.expr, trans))
    if isinstance(e, Add):
        return Add(push_transposes(e.left, trans), push_transposes(e.right, trans), e.sign)
    if isinstance(e, MatMul):
        if trans:
            return MatMul(push_transposes(e.right, True), push_transposes(e.left, True))
        return MatMul(push_transposes(e.left), push_transposes(e.right))
    if isinstance(e, Call):
        call = Call(e.name, [push_transposes(a) for a in e.args], e.shape, e.node)
        return Transpose(call) if trans else call
    raise TypeError(e)


def split_coef(e):
    """e = coef * core, with core not a Scale."""
    coef = ONE
    while isinstance(e, Scale):
        coef = coef * e.coef
        e = e.expr
    return coef, e


def terms(e, coef=ONE):
    """Expand e (with transposes pushed down) into a list of (coef, term),
    where a term is a Leaf, a MatMul of two operands, a Call or a transposed
    Call."""
    if isinstance(e, Scale):
        return terms(e.expr, coef * e.coef)
    if isinstance(e, Add):
        return terms(e.left, coef) + terms(e.right, coef * Coef(e.sign))
    if isinstance(e, MatMul):
        cl, left = split_coef(e.left)
        cr, right = split_coef(e.right)
        return [(coef * cl * cr, MatMul(left, right))]
    return [(coef, e)]


def same_matrix(a, b):
    return ast.dump(load(a)) == ast.dump(load(b))


def is_block(node):
    """Whether node is a block A[a:b, c:d] of a matrix."""
    return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Tuple) and \
        any(isinstance(i, ast.Slice) for i in node.slice.elts)


def split_block(node):
    """(matrix, row slice, column slice) of a block, (node, None, None) for
    a whole matrix."""
    if is_block(node):
        return node.value, node.slice.elts[0], node.slice.elts[1]
    return node, None, None


def may_alias(a, b):
    """Whether the matrices or blocks a and b (variables, attributes, List
    elements) can overlap. Elements of the same List are distinct if their
    indices are k + c1 and k + c2 (or constants) with c1 != c2; blocks of
    the same matrix are distinct if their rows or columns are disjoint
    ranges of constants (or of k + constant)."""
    a, ra, ca = split_block(a)
    b, rb, cb = split_block(b)
    if not same_base(a, b):
        return False
    return ranges_may_overlap(ra, rb) and ranges_may_overlap(ca, cb)


def same_base(a, b):
    if same_matrix(a, b):
        return True
    if isinstance(a, ast.Subscript) and isinstance(b, ast.Subscript) and \
            same_matrix(a.value, b.value):
        ia, ib = affine_index(a.slice), affine_index(b.slice)
        if ia is None or ib is None:
            return True
        return ia[0] == ib[0] and ia[1] == ib[1]
    return False


def ranges_may_overlap(a, b):
    """Whether two slices (None: the whole range) can overlap."""
    if a is None or b is None or None in (a.lower, a.upper, b.lower, b.upper):
        return True
    bounds = [affine_index(x) for x in (a.lower, a.upper, b.lower, b.upper)]
    if None in bounds or len({v for v, c in bounds}) > 1:
        return True
    al, au, bl, bu = [c for v, c in bounds]
    return al < bu and bl < au


def affine_index(node):
    """(variable name or None, constant) for indices k, k + c, k - c, c."""
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return (None, node.value)
    if isinstance(node, ast.Name):
        return (node.id, 0)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)) and \
            isinstance(node.left, ast.Name) and isinstance(node.right, ast.Constant) and \
            type(node.right.value) is int:
        return (node.left.id, node.right.value if isinstance(node.op, ast.Add) else -node.right.value)
    return None


def load(node):
    node = deepcopy(node)
    for n in ast.walk(node):
        if hasattr(n, 'ctx'):
            n.ctx = ast.Load()
    return node


def call(name, *args):
    return ast.Expr(ast.Call(func=ast.Name(name, ast.Load()), args=list(args), keywords=[]))


class Temporaries:
    """Temporary matrices of a function, reused across statements."""

    def __init__(self, prefix):
        self.prefix = prefix
        self.matrices = []  # (name, shape)
        self.busy = set()
        self.scalars = 0

    def matrix(self, shape, node):
        if shape[0].value is None or shape[1].value is None:
            raise LoweringError(node, 'this expression needs a temporary matrix whose size is '
                'not known at compile time (an operand is a function argument): assign the '
                'subexpression to a declared matrix first')
        for name, s in self.matrices:
            if name not in self.busy and s[0] == shape[0] and s[1] == shape[1]:
                self.busy.add(name)
                return ast.Name(name, ast.Load())
        name = '{}m{}'.format(self.prefix, len(self.matrices))
        self.matrices.append((name, shape))
        self.busy.add(name)
        return ast.Name(name, ast.Load())

    def scalar(self):
        self.scalars += 1
        return '{}s{}'.format(self.prefix, self.scalars)

    def release(self):
        self.busy = set()

    def declarations(self):
        return [ast.AnnAssign(target=ast.Name(name, ast.Store()),
            annotation=ast.Name('pmat', ast.Load()),
            value=ast.Call(func=ast.Name('pmat', ast.Load()),
                args=[shape[0].expr(), shape[1].expr()], keywords=[]),
            simple=1) for name, shape in self.matrices]


class Lowering:
    """Lower one assignment target = expr."""

    def __init__(self, temps, dims=None):
        self.temps = temps
        # values of the dims constants: indices made of dims constants are
        # passed as literals (in C, dims constants are macros)
        self.dims = dims or {}
        self.out = []

    def emit(self, stmt):
        self.out.append(stmt)

    # scalar factors

    def coef_value(self, coef):
        """An expression for coef: a literal or a variable."""
        if not coef.factors:
            return ast.Constant(float(coef.const))
        value = coef.factors[0]
        for f in coef.factors[1:]:
            value = ast.BinOp(left=value, op=ast.Mult(), right=f)
        if coef.const != 1.0:
            value = ast.BinOp(left=ast.Constant(float(coef.const)), op=ast.Mult(), right=value)
        if isinstance(value, ast.Name):
            return value
        name = self.temps.scalar()
        self.emit(ast.AnnAssign(target=ast.Name(name, ast.Store()),
            annotation=ast.Name('float', ast.Load()), value=value, simple=1))
        return ast.Name(name, ast.Load())

    def hoist_factors(self, e):
        """Compute the scalar factors that are not literals or variables
        before anything is written."""
        if isinstance(e, Scale):
            factors = []
            for f in e.coef.factors:
                if isinstance(f, (ast.Name, ast.Constant)):
                    factors.append(f)
                else:
                    name = self.temps.scalar()
                    self.emit(ast.AnnAssign(target=ast.Name(name, ast.Store()),
                        annotation=ast.Name('float', ast.Load()), value=load(f), simple=1))
                    factors.append(ast.Name(name, ast.Load()))
            return Scale(Coef(e.coef.const, factors), self.hoist_factors(e.expr))
        if isinstance(e, Transpose):
            return Transpose(self.hoist_factors(e.expr))
        if isinstance(e, Add):
            return Add(self.hoist_factors(e.left), self.hoist_factors(e.right), e.sign)
        if isinstance(e, MatMul):
            return MatMul(self.hoist_factors(e.left), self.hoist_factors(e.right))
        if isinstance(e, Call):
            return Call(e.name, [self.hoist_factors(a) for a in e.args], e.shape, e.node)
        return e

    # assignment

    def assign(self, target, target_shape, expr):
        expr = push_transposes(self.hoist_factors(expr))
        ts = terms(expr)
        # target = target + ...: accumulate in place, unless the target is
        # also read elsewhere
        inplace = [i for i, (c, t) in enumerate(ts) if isinstance(t, Leaf) and not t.trans
            and same_matrix(t.node, target)]
        reads = [l for i, (c, t) in enumerate(ts) if i not in inplace[:1] for l in leaves(t)]
        if len(inplace) > 1 or any(may_alias(l.node, target) for l in reads):
            tmp = self.temps.matrix(target_shape, target)
            self.evaluate(tmp, expr)
            self.copy(tmp, target)
        else:
            self.evaluate(target, expr, ts)

    def evaluate(self, dest, expr, ts=None):
        """dest = expr, where dest is not read by expr (except as a term
        dest + ...)."""
        if ts is None:
            ts = terms(expr)
        # initialize with: the term dest itself, then matrices and calls, then products
        def rank(item):
            c, t = item
            if isinstance(t, Leaf) and not t.trans and same_matrix(t.node, dest):
                return 0
            return 2 if isinstance(t, MatMul) else 1
        ts = sorted(ts, key=rank)
        for i, (coef, term) in enumerate(ts):
            if i == 0:
                self.initialize(dest, coef, term)
            else:
                self.accumulate(dest, coef, term)

    # operations on matrices or blocks: a block A[a:b, c:d] is passed as
    # A, a, c, b - a, d - c to the _view variants of the routines (a whole
    # matrix as A, 0, 0, -1, -1)

    def index(self, node):
        value = eval_dims(node, self.dims)
        return ast.Constant(value) if value is not None else load(node)

    def view(self, node):
        # (M, first row, first column, rows, columns); -1: to the end
        base, rows, cols = split_block(node)
        if rows is None:
            return [load(node), ast.Constant(0), ast.Constant(0), ast.Constant(-1), ast.Constant(-1)]
        args = [load(base)]
        for s in (rows, cols):
            args.append(self.index(s.lower) if s.lower is not None else ast.Constant(0))
        for s in (rows, cols):
            lo, up = (affine_index(x) if x is not None else None for x in (s.lower, s.upper))
            if s.upper is None:
                # to the end
                args.append(ast.Constant(-1))
            elif s.lower is None:
                args.append(self.index(s.upper))
            elif lo is not None and up is not None and lo[0] == up[0]:
                # k + c2 - (k + c1)
                args.append(ast.Constant(up[1] - lo[1]))
            else:
                args.append(self.index(ast.BinOp(left=s.upper, op=ast.Sub(), right=s.lower)))
        return args

    def matrix_call(self, name, before, mats):
        """name(*before, *mats), or its _view variant if one of the matrices
        is a block."""
        if any(is_block(m) for m in mats):
            self.emit(call(name + '_view', *(list(before) + [a for m in mats for a in self.view(m)])))
        else:
            self.emit(call(name, *(list(before) + [load(m) for m in mats])))

    def copy(self, src, dest):
        self.matrix_call('pmat_copy', [], [src, dest])

    def tran(self, src, dest):
        self.matrix_call('pmat_tran', [], [src, dest])

    def fill(self, dest, value):
        if is_block(dest):
            self.emit(call('pmat_fill_view', ast.Constant(value), *self.view(dest)))
        else:
            self.emit(call('pmat_fill', load(dest), ast.Constant(value)))

    def gead(self, alpha, src, dest):
        self.matrix_call('pmt_gead', [alpha], [src, dest])

    def gemm(self, trans, alpha, a, b, dest):
        """dest += alpha * op(a) op(b)."""
        name = 'pmt_gemm_' + ('view_' if is_block(a) or is_block(b) or is_block(dest) else 'ab_') + trans
        if name.startswith('pmt_gemm_view'):
            args = [alpha] + self.view(a) + self.view(b) + [ast.Constant(1.0)] + self.view(dest) + \
                self.view(dest)
        else:
            args = [alpha, load(a), load(b), ast.Constant(1.0), load(dest), load(dest)]
        self.emit(call(name, *args))

    def scale(self, dest, coef):
        if not coef.is_one():
            alpha = self.coef_value(coef)
            if is_block(dest):
                self.emit(call('pmat_scale_view', alpha, *self.view(dest)))
            else:
                self.emit(call('pmat_scale', alpha, load(dest)))

    def initialize(self, dest, coef, term):
        if isinstance(term, Leaf):
            if not term.trans and same_matrix(term.node, dest):
                pass
            elif term.trans:
                self.tran(term.node, dest)
            else:
                self.copy(term.node, dest)
            self.scale(dest, coef)
        elif isinstance(term, MatMul):
            self.fill(dest, 0.0)
            self.product(dest, coef, term)
        elif isinstance(term, Transpose):
            tmp = self.temps.matrix(term.expr.shape, term.expr.node)
            self.function(tmp, term.expr)
            self.tran(tmp, dest)
            self.scale(dest, coef)
        else:
            self.function(dest, term)
            self.scale(dest, coef)

    def accumulate(self, dest, coef, term):
        if isinstance(term, MatMul):
            self.product(dest, coef, term)
            return
        if isinstance(term, Leaf) and not term.trans:
            src = term.node
        else:
            src = self.temps.matrix(term.shape, getattr(term, 'node', dest))
            self.initialize(src, ONE, term)
        self.gead(self.coef_value(coef), src, dest)

    def operand(self, e):
        """A (possibly transposed) matrix holding the value of e."""
        if isinstance(e, Leaf):
            return e.node, e.trans
        if isinstance(e, Transpose):
            tmp = self.temps.matrix(e.expr.shape, e.expr.node)
            self.function(tmp, e.expr)
            return tmp, True
        tmp = self.temps.matrix(e.shape, getattr(e, 'node', None))
        self.evaluate(tmp, e)
        return tmp, False

    def product(self, dest, coef, term):
        """dest += coef * left @ right."""
        a, ta = self.operand(term.left)
        b, tb = self.operand(term.right)
        self.gemm(('t' if ta else 'n') + ('t' if tb else 'n'), self.coef_value(coef), a, b, dest)

    def function(self, dest, e):
        if is_block(dest):
            # the factorizations work on whole matrices
            tmp = self.temps.matrix(e.shape, e.node)
            self.function(tmp, e)
            self.copy(tmp, dest)
            return
        if e.name == 'cholesky':
            a, ta = self.operand(e.args[0])
            if ta or is_block(a):
                tmp = self.temps.matrix(e.shape, e.node)
                self.initialize(tmp, ONE, Leaf(a, e.shape, ta))
                a = tmp
            # cholesky gives a lower triangular matrix, as in NumPy
            self.fill(dest, 0.0)
            self.emit(call('pmt_potrf', load(a), load(dest)))
        elif e.name == 'cho_solve':
            # pmt_potrsm overwrites the upper triangle of the factor: solve
            # with a copy, so that L is unchanged (as in SciPy)
            fact = self.temps.matrix(e.args[0].shape, e.node)
            self.evaluate(fact, e.args[0])
            self.evaluate(dest, e.args[1])
            self.emit(call('pmt_potrsm', fact, load(dest)))
        else:
            raise TypeError(e.name)


class Plan:
    """An assignment target = expr to lower; fun is the position of the
    enclosing function."""

    def __init__(self, stmt, target, target_shape, expr, fun, dims=None):
        self.stmt = stmt
        self.target = target
        self.target_shape = target_shape
        self.expr = expr
        self.fun = fun
        self.dims = dims


def lower_statement(plan, temps):
    lowering = Lowering(temps, plan.dims)
    lowering.assign(plan.target, plan.target_shape, plan.expr)
    temps.release()
    for stmt in lowering.out:
        ast.copy_location(stmt, plan.stmt)
    return lowering.out


def position(node):
    return (node.lineno, node.col_offset)


TEMP_PREFIX = '___pmt_'


def lower(tree, plans):
    """Replace the assignments of matrix expressions in tree (plans: position
    -> Plan, from the checker) with calls; declare the temporaries at the
    beginning of each function."""
    if not plans:
        return tree
    for fun in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        temps = Temporaries(TEMP_PREFIX)
        fun.body = lower_block(fun.body, plans, temps)
        fun.body = [ast.copy_location(d, fun.body[0]) for d in temps.declarations()] + fun.body
    return ast.fix_missing_locations(tree)


def lower_block(stmts, plans, temps):
    out = []
    for stmt in stmts:
        if isinstance(stmt, ast.Assign) and position(stmt) in plans:
            out.extend(lower_statement(plans[position(stmt)], temps))
            continue
        for field in ('body', 'orelse'):
            if isinstance(stmt, (ast.For, ast.While, ast.If)):
                setattr(stmt, field, lower_block(getattr(stmt, field), plans, temps))
        out.append(stmt)
    return out


class StripAnnotations(ast.NodeTransformer):
    """Remove type annotations, to run lowered code in Python."""

    def visit_AnnAssign(self, node):
        if node.value is None:
            return ast.copy_location(ast.Pass(), node)
        return ast.copy_location(ast.Assign(targets=[node.target], value=node.value), node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        for arg in node.args.args:
            arg.annotation = None
        node.returns = None
        return node
