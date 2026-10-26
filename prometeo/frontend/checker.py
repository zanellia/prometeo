"""Static checker for prometeo programs.

The checker runs before a program is executed (Python mode) or transpiled
(C mode). It accepts exactly the language described in docs/source/language/language.rst:
every statement and expression form must be explicitly allowed here, and
every expression gets a type. Anything else is reported with its source
location, so that unsupported code is rejected up front instead of failing
(or, worse, behaving differently) later.
"""

import ast
import re
from copy import deepcopy

from .types import Type, INT, FLOAT, DIMS, DIMV, STR, NONE, PMAT, PVEC, \
    list_of, is_list, is_int_like, is_scalar, LIST_ELEMENT_TYPES
from .normalize import normalize, eval_dims
from .matexpr import Dim, UNKNOWN, Leaf, Scale, Add, MatMul, Transpose, Call, Coef, Plan, \
    Temporaries, LoweringError, MATRIX_FUNCTIONS, TEMP_PREFIX, lower_statement, position
from .builtins import BUILTINS, UNSUPPORTED_BUILTINS, OUTPUT_ALIASING, BUILTIN_KEYWORDS

C_KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'inline',
    'int', 'long', 'register', 'restrict', 'return', 'short', 'signed',
    'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned',
    'void', 'volatile', 'while', 'NULL', 'printf', 'malloc', 'free', 'dims',
    'dimv', 'pmat', 'pvec', 'List', 'plist', 'range', 'print', 'self',
}
RESERVED_PREFIXES = ('c_pmt_', '_c_pmt_', '___c_pmt', '___pmt', 'blasfeo_', '_Z')

# scalar functions (sin, cos, ... on floats; abs, min, max on ints or floats)
# -> number of arguments
MATH_FUNCTIONS = {'sin': 1, 'cos': 1, 'tan': 1, 'exp': 1, 'log': 1, 'sqrt': 1,
    'abs': 1, 'min': 2, 'max': 2}


class Diagnostic:
    def __init__(self, severity, lineno, col, message):
        self.severity = severity
        self.lineno = lineno
        self.col = col
        self.message = message

    def __str__(self):
        return '{}:{}: {}: {}'.format(self.lineno, self.col + 1, self.severity, self.message)

    __repr__ = __str__


class FunctionInfo:
    def __init__(self, name, arg_names, arg_types, ret_type, node):
        self.name = name
        self.arg_names = arg_names
        self.arg_types = arg_types
        self.ret_type = ret_type
        self.node = node


class ClassInfo:
    def __init__(self, name, node):
        self.name = name
        self.node = node
        self.attrs = {}
        # shapes of pmat attributes, dimv constants sizing Lists of pmat
        self.shapes = {}
        self.list_sizes = {}
        self.methods = {}


class Scope:
    """Variables visible in a function body. Blocks (loop and if bodies) open
    nested scopes, as in C."""

    def __init__(self, fun, cls):
        self.fun = fun
        self.cls = cls
        self.blocks = [{}]
        # all the variables declared in the function, in any block
        self.declared = {}
        self.loop_vars = []
        # shapes of the pmat variables
        self.shapes = {}
        self.depth = 0  # nesting depth of loops and conditionals
        self.loops = 0  # nesting depth of loops

    def lookup(self, name):
        for block in reversed(self.blocks):
            if name in block:
                return block[name]
        return None

    def declare(self, name, t):
        self.blocks[-1][name] = t

    def push(self):
        self.blocks.append({})
        self.depth += 1

    def pop(self):
        self.blocks.pop()
        self.depth -= 1


class Checker:

    def __init__(self, casadi_functions=None):
        # CasADi functions defined in pure blocks: name -> (inputs, outputs)
        self.casadi_functions = casadi_functions or {}
        self.diagnostics = []
        self.globals = {}
        self.functions = {}
        self.classes = {}
        self.global_names = set()
        # values of dims constants, [rows, cols] pairs of dimv constants
        self.dims_values = {}
        self.dimv_values = {}
        # assignments of matrix expressions: position -> Plan
        self.plans = {}

    # diagnostics

    def error(self, node, message):
        self.diagnostics.append(Diagnostic('error', getattr(node, 'lineno', 1),
            getattr(node, 'col_offset', 0), message))

    def warning(self, node, message):
        self.diagnostics.append(Diagnostic('warning', getattr(node, 'lineno', 1),
            getattr(node, 'col_offset', 0), message))

    def unsupported(self, node, what, hint=None):
        message = 'not supported (yet): ' + what
        if hint:
            message += '; ' + hint
        self.error(node, message)

    def check_identifier(self, node, name, declaring_global=False):
        if name in self.casadi_functions:
            self.error(node, "'{}' is a CasADi function and cannot be redefined".format(name))
        elif name in self.global_names and not declaring_global:
            self.error(node, "'{}' is a module-level constant: its name cannot be reused (in C, "
                "dims constants are macros)".format(name))
        elif name in C_KEYWORDS:
            self.error(node, "'{}' is reserved and cannot be used as a name".format(name))
        elif name.startswith(RESERVED_PREFIXES):
            self.error(node, "names starting with '{}' are reserved".format(
                [p for p in RESERVED_PREFIXES if name.startswith(p)][0]))
        elif name in BUILTINS or name in UNSUPPORTED_BUILTINS or name in MATH_FUNCTIONS \
                or name in MATRIX_FUNCTIONS:
            self.error(node, "'{}' is a built-in function and cannot be redefined".format(name))

    # module

    def check_module(self, tree):
        # names of module-level constants
        self.global_names = {stmt.target.id for stmt in tree.body
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)}
        for stmt in tree.body:
            if isinstance(stmt, ast.ImportFrom):
                if stmt.module != 'prometeo' or len(stmt.names) != 1 or \
                        stmt.names[0].name != '*':
                    self.error(stmt, "only 'from prometeo import *' can be imported "
                        "(use '# pure >' ... '# pure <' blocks for Python-only code)")
            elif isinstance(stmt, ast.AnnAssign):
                self.declare_global(stmt)
            elif isinstance(stmt, ast.FunctionDef):
                self.declare_function(stmt, self.functions, None)
            elif isinstance(stmt, ast.ClassDef):
                self.declare_class(stmt)
            elif isinstance(stmt, ast.Import):
                self.error(stmt, "only 'from prometeo import *' can be imported "
                    "(use '# pure >' ... '# pure <' blocks for Python-only code)")
            else:
                self.unsupported(stmt, '{} at module level'.format(describe(stmt)))

        if 'main' not in self.functions:
            self.error(tree, "missing 'def main() -> int' function")
        else:
            main = self.functions['main'][0]
            if main.arg_types or main.ret_type != INT:
                self.error(main.node, "main must be defined as 'def main() -> int'")

        for cls in self.classes.values():
            for overloads in cls.methods.values():
                for method in overloads:
                    self.check_function_body(method, cls)
        for overloads in self.functions.values():
            for fun in overloads:
                self.check_function_body(fun, None)

    def declare_global(self, stmt):
        if not isinstance(stmt.target, ast.Name) or not isinstance(stmt.annotation, ast.Name):
            self.unsupported(stmt, 'this module-level declaration')
            return
        name = stmt.target.id
        self.check_identifier(stmt.target, name, declaring_global=True)
        if name in self.globals:
            self.error(stmt, "'{}' is already defined".format(name))
        ann = stmt.annotation.id
        if stmt.value is None:
            self.error(stmt, "module-level constant '{}' must be initialized".format(name))
            return
        if ann == 'dims':
            if self.constant_expr(stmt.value, int_only=True) is not None:
                self.globals[name] = DIMS
                self.dims_values[name] = eval_dims(stmt.value, self.dims_values)
        elif ann == 'dimv':
            if self.check_dimv(stmt.value):
                self.globals[name] = DIMV
                self.dimv_values[name] = [(self.dim(pair.elts[0]), self.dim(pair.elts[1]))
                    for pair in stmt.value.elts]
        elif ann in ('int', 'float'):
            t = self.constant_expr(stmt.value, int_only=ann == 'int')
            if t is not None:
                self.globals[name] = INT if ann == 'int' else FLOAT
        else:
            self.error(stmt, "module-level declarations must have type dims, dimv, "
                "int or float, not '{}'".format(ann))

    def constant_expr(self, node, int_only):
        """Expression made of numeric literals and module-level constants."""
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if int_only and type(node.value) is not int:
                self.error(node, 'expected an integer value')
                return None
            return INT if type(node.value) is int else FLOAT
        if isinstance(node, ast.Name):
            t = self.globals.get(node.id)
            if t is None:
                self.error(node, "'{}' is not a module-level constant defined above".format(node.id))
                return None
            if int_only and not is_int_like(t):
                self.error(node, "'{}' is not an integer constant".format(node.id))
                return None
            return t
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            left = self.constant_expr(node.left, int_only)
            right = self.constant_expr(node.right, int_only)
            if left is None or right is None:
                return None
            if is_int_like(left) != is_int_like(right):
                self.error(node, 'mixed int/float arithmetic is not supported: use float literals (e.g. 2.0)')
                return None
            return INT if is_int_like(left) else FLOAT
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return self.constant_expr(node.operand, int_only)
        self.error(node, 'expected a constant expression (literals, module-level constants, +, -, *)')
        return None

    def check_dimv(self, node):
        if not isinstance(node, ast.List) or not node.elts:
            self.error(node, 'dimv must be a list of [rows, cols] pairs')
            return False
        ok = True
        for pair in node.elts:
            if not isinstance(pair, ast.List) or len(pair.elts) != 2:
                self.error(pair, 'dimv must be a list of [rows, cols] pairs')
                ok = False
                continue
            for dim in pair.elts:
                ok = self.constant_expr(dim, int_only=True) is not None and ok
        return ok

    # declarations

    def annotation_type(self, node, what, allow_none=False):
        if allow_none and isinstance(node, ast.Constant) and node.value is None:
            return NONE
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id in ('pmat', 'pvec'):
            return PMAT if node.value.id == 'pmat' else PVEC
        if not isinstance(node, ast.Name):
            self.error(node, '{} must be a type name'.format(what))
            return None
        name = node.id
        if name == 'None' and allow_none:
            return NONE
        if name in ('int', 'float', 'pmat', 'pvec'):
            return {'int': INT, 'float': FLOAT, 'pmat': PMAT, 'pvec': PVEC}[name]
        if name == 'List':
            return list_of(None)
        if name in self.classes:
            return Type(name)
        if name in ('dims', 'dimv'):
            self.error(node, "'{}' can only be used for module-level constants".format(name))
            return None
        self.error(node, "unknown type '{}'".format(name))
        return None

    def declare_function(self, node, table, cls):
        if node.decorator_list:
            self.unsupported(node.decorator_list[0], 'decorators')
        args = node.args
        if args.posonlyargs or args.vararg or args.kwonlyargs or args.kwarg or args.defaults:
            self.unsupported(node, 'default values, *args and **kwargs',
                'only plain positional arguments can be used')
        arg_list = list(args.args)
        if cls is not None:
            if not arg_list or arg_list[0].arg != 'self':
                self.error(node, "the first argument of method '{}' must be 'self'".format(node.name))
                return
            if arg_list[0].annotation is not None:
                self.error(arg_list[0], "'self' must not be annotated")
            arg_list = arg_list[1:]
        else:
            self.check_identifier(node, node.name)
        arg_names = []
        arg_types = []
        for arg in arg_list:
            self.check_identifier(arg, arg.arg)
            if arg.annotation is None:
                self.error(arg, "argument '{}' needs a type annotation".format(arg.arg))
                t = None
            else:
                t = self.annotation_type(arg.annotation, "the annotation of '{}'".format(arg.arg))
            arg_names.append(arg.arg)
            arg_types.append(t)
        if node.returns is None:
            self.error(node, "function '{}' needs a return type annotation".format(node.name))
            ret_type = None
        else:
            ret_type = self.annotation_type(node.returns, 'the return annotation', allow_none=True)
            if ret_type is not None and (is_list(ret_type) or ret_type.name in self.classes):
                self.unsupported(node.returns, 'returning {} values'.format(ret_type.name))
        info = FunctionInfo(node.name, arg_names, arg_types, ret_type, node)
        overloads = table.setdefault(node.name, [])
        for other in overloads:
            if other.arg_types == arg_types:
                self.error(node, "'{}' is already defined with the same argument types".format(node.name))
                return
        if overloads:
            self.warning(node, "'{}' is overloaded: this works in transpiled code, but in "
                "Python only the last definition is used".format(node.name))
        overloads.append(info)

    def declare_class(self, node):
        self.check_identifier(node, node.name)
        if node.bases or node.keywords:
            self.unsupported(node, 'class inheritance')
        if node.decorator_list:
            self.unsupported(node.decorator_list[0], 'decorators')
        if node.name in self.classes:
            self.error(node, "class '{}' is already defined".format(node.name))
            return
        cls = ClassInfo(node.name, node)
        # register the class first: attributes and methods can use its type
        self.classes[node.name] = cls
        for stmt in node.body:
            if not isinstance(stmt, ast.FunctionDef):
                self.unsupported(stmt, '{} in a class body'.format(describe(stmt)))
                continue
            if stmt.name.startswith('__') and stmt.name != '__init__':
                self.unsupported(stmt, "special method '{}'".format(stmt.name))
                continue
            self.declare_function(stmt, cls.methods, cls)
        init = cls.methods.get('__init__')
        if init:
            if len(init) > 1 or init[0].arg_types:
                self.error(init[0].node, "the constructor must be defined as "
                    "'def __init__(self) -> None'")
            for stmt in init[0].node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute) \
                        and isinstance(stmt.target.value, ast.Name) \
                        and stmt.target.value.id == 'self':
                    t = self.annotation_type(stmt.annotation, 'the attribute annotation')
                    if is_list(t) and stmt.value is not None:
                        # the element type is given by the plist constructor
                        t = self.check_constructor(stmt.value, t)
                    if t is not None:
                        self.check_identifier(stmt.target, stmt.target.attr)
                        cls.attrs[stmt.target.attr] = t
                        if t == PMAT:
                            cls.shapes[stmt.target.attr] = self.constructor_shape(stmt.value)
                        elif is_list(t) and t.elem == PMAT and isinstance(stmt.value.args[1], ast.Name):
                            cls.list_sizes[stmt.target.attr] = stmt.value.args[1].id

    # function bodies

    def check_function_body(self, fun, cls):
        scope = Scope(fun, cls)
        for name, t in zip(fun.arg_names, fun.arg_types):
            scope.declare(name, t)
        self.check_block(fun.node.body, scope)
        if fun.ret_type not in (None, NONE) and not ends_with_return(fun.node.body):
            self.error(fun.node, "function '{}' must end with a return statement".format(fun.name))

    def check_block(self, stmts, scope):
        for stmt in stmts:
            self.check_stmt(stmt, scope)

    def check_stmt(self, stmt, scope):
        if isinstance(stmt, ast.AnnAssign):
            self.check_declaration(stmt, scope)
        elif isinstance(stmt, ast.Assign):
            self.check_assignment(stmt, scope)
        elif isinstance(stmt, ast.Expr):
            self.check_expression_statement(stmt, scope)
        elif isinstance(stmt, ast.For):
            self.check_for(stmt, scope)
        elif isinstance(stmt, ast.While):
            if stmt.orelse:
                self.unsupported(stmt, "'else' on loops")
            self.check_condition(stmt.test, scope)
            scope.push()
            scope.loops += 1
            self.check_block(stmt.body, scope)
            scope.loops -= 1
            scope.pop()
        elif isinstance(stmt, ast.If):
            self.check_condition(stmt.test, scope)
            scope.push()
            self.check_block(stmt.body, scope)
            scope.pop()
            scope.push()
            self.check_block(stmt.orelse, scope)
            scope.pop()
        elif isinstance(stmt, ast.Return):
            self.check_return(stmt, scope)
        elif isinstance(stmt, (ast.Break, ast.Continue)):
            if scope.loops == 0:
                self.error(stmt, '{} outside a loop'.format(describe(stmt)))
        elif isinstance(stmt, ast.Pass):
            pass
        else:
            self.unsupported(stmt, describe(stmt))

    def check_declaration(self, stmt, scope):
        target = stmt.target
        if isinstance(target, ast.Attribute):
            if scope.fun.name != '__init__' or scope.cls is None or \
                    not (isinstance(target.value, ast.Name) and target.value.id == 'self'):
                self.error(stmt, 'attributes can only be declared in __init__, as self.<name>: <type> = <value>')
                return
            t = scope.cls.attrs.get(target.attr)
            name = 'self.' + target.attr
        elif isinstance(target, ast.Name):
            name = target.id
            self.check_identifier(target, name)
            if name in scope.blocks[-1] or (len(scope.blocks) == 1 and name in scope.fun.arg_names):
                self.error(stmt, "'{}' is already declared".format(name))
                return
            if scope.lookup(name) is not None or name in scope.loop_vars:
                self.error(stmt, "'{}' shadows a variable declared in an enclosing block".format(name))
                return
            t = self.annotation_type(stmt.annotation, "the annotation of '{}'".format(name))
            if t is not None and scope.declared.get(name, t) != t:
                self.error(stmt, "'{}' was declared as {} in another block of this function: "
                    "declare it with the same type, or use another name".format(name, scope.declared[name]))
                return
            if t is not None:
                scope.declared[name] = t
        else:
            self.unsupported(stmt, 'this declaration')
            return
        if t is None:
            return
        if stmt.value is None:
            self.error(stmt, "'{}' must be initialized".format(name))
            return
        if t in (PMAT, PVEC) or is_list(t) or t.name in self.classes:
            if is_list(t) and isinstance(target, ast.Name):
                t = self.check_constructor(stmt.value, t)
                if t is not None and t.elem in (PMAT, PVEC):
                    self.unsupported(stmt, 'Lists of {} as local variables'.format(t.elem),
                        'declare the List as a class attribute')
                    return
                if t is not None:
                    scope.declare(name, t)
                return
            if scope.depth > 0:
                self.error(stmt, 'matrices, vectors, lists and objects must be declared outside '
                    'loops and conditionals: each declaration allocates memory, so in a loop the '
                    'program would use more memory than the computed bound')
            t = self.check_constructor(stmt.value, t)
            if t == PMAT and isinstance(target, ast.Name):
                scope.shapes[name] = self.constructor_shape(stmt.value)
        elif t in (INT, FLOAT):
            self.check_scalar_value(stmt.value, t, scope)
        if t is not None and isinstance(target, ast.Name):
            scope.declare(name, t)

    def check_constructor(self, value, t):
        """Value of a declaration of a matrix, vector, list or object."""
        call_name = value.func.id if isinstance(value, ast.Call) and \
            isinstance(value.func, ast.Name) else None
        if t == PMAT:
            if call_name != 'pmat' or len(value.args) != 2 or value.keywords:
                self.error(value, 'a pmat must be initialized with pmat(<rows>, <cols>)')
                return None
            for arg in value.args:
                self.check_dims(arg)
            return PMAT
        if t == PVEC:
            if call_name != 'pvec' or len(value.args) != 1 or value.keywords:
                self.error(value, 'a pvec must be initialized with pvec(<size>)')
                return None
            self.check_dims(value.args[0])
            return PVEC
        if is_list(t):
            if call_name != 'plist' or len(value.args) != 2 or value.keywords:
                self.error(value, 'a List must be initialized with plist(<type>, <sizes>)')
                return None
            elem_node, sizes = value.args
            elem_name = elem_node.id if isinstance(elem_node, ast.Name) else \
                elem_node.value if isinstance(elem_node, ast.Constant) else None
            elem = LIST_ELEMENT_TYPES.get(elem_name)
            if elem is None:
                self.error(elem_node, 'the element type of a List must be one of pmat, pvec, int, float')
                return None
            if elem in (PMAT, PVEC):
                if not (isinstance(sizes, ast.Name) and self.globals.get(sizes.id) == DIMV):
                    self.error(sizes, 'the sizes of a List of {} must be a module-level dimv constant'.format(elem))
                    return None
            else:
                self.check_dims(sizes)
            return list_of(elem)
        # object
        if call_name != t.name or value.args or value.keywords:
            self.error(value, "an object of class '{}' must be initialized with {}()".format(t.name, t.name))
            return None
        return t

    def check_dims(self, node):
        """Matrix and vector sizes must be dims expressions."""
        t = self.dims_expr(node)
        if t is None:
            return

    def dims_expr(self, node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return INT
        if isinstance(node, ast.Name):
            t = self.globals.get(node.id)
            if t is None:
                self.error(node, "'{}' is not a module-level dims constant".format(node.id))
                return None
            if t != DIMS:
                self.error(node, "sizes must be dims constants, '{}' is {}".format(node.id, t))
                return None
            return DIMS
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
            left = self.dims_expr(node.left)
            right = self.dims_expr(node.right)
            if left is None or right is None:
                return None
            return DIMS if DIMS in (left, right) else INT
        self.error(node, 'sizes must be dims constants or +, -, * combinations of them')
        return None

    # assignments

    def check_assignment(self, stmt, scope):
        if len(stmt.targets) != 1 or isinstance(stmt.targets[0], (ast.Tuple, ast.List)):
            self.unsupported(stmt, 'multiple assignment')
            return
        target = stmt.targets[0]
        value = stmt.value
        if isinstance(target, ast.Name):
            if target.id in scope.loop_vars and scope.lookup(target.id) is None:
                self.error(target, "cannot assign to loop variable '{}'".format(target.id))
                return
            t = scope.lookup(target.id)
            if t is None:
                if target.id in self.globals:
                    self.error(target, "cannot assign to module-level constant '{}'".format(target.id))
                else:
                    self.error(target, "'{}' must be declared before it is assigned, "
                        "e.g. '{}: float = 0.0'".format(target.id, target.id))
                return
            if is_scalar(t):
                self.check_scalar_value(value, t, scope)
            elif t in (PMAT, PVEC):
                self.check_matrix_value(stmt, value, t, scope, target)
            else:
                self.unsupported(stmt, 'assigning to a variable of type {}'.format(t))
        elif isinstance(target, ast.Subscript):
            self.check_subscript_assignment(stmt, target, value, scope)
        elif isinstance(target, ast.Attribute):
            t = self.attribute_type(target, scope)
            if t is None:
                return
            if t == PMAT and self.is_matrix_expression(value, scope):
                self.check_matrix_expression(stmt, target, value, scope)
                return
            if not is_scalar(t):
                self.unsupported(stmt, 'assigning to an attribute of type {}'.format(t),
                    'modify it in place instead (e.g. with {}_copy)'.format(t) if t in (PMAT, PVEC) else None)
                return
            self.check_scalar_value(value, t, scope)
        else:
            self.unsupported(stmt, 'assigning to {}'.format(describe(target)))

    def check_scalar_value(self, value, t, scope):
        """Right-hand side assigned to a scalar of type t."""
        if isinstance(value, ast.Constant) and type(value.value) is int and t == FLOAT:
            return
        self.check_evaluation_order(value, scope)
        vt = self.scalar_expr(value, scope)
        if vt is None:
            return
        if not same_scalar(vt, t):
            self.error(value, 'cannot assign a value of type {} to a variable of type {}'.format(vt, t))

    def check_matrix_value(self, stmt, value, t, scope, target):
        """Right-hand side assigned to the pmat or pvec variable target."""
        if isinstance(value, ast.Name):
            self.error(value, "'B = A' would make two {} variables share their data, which behaves "
                "differently in Python and in C: use {}_copy(A, B)".format(t, t))
            return
        if t == PMAT and self.is_matrix_expression(value, scope):
            self.check_matrix_expression(stmt, target, value, scope)
            return
        if isinstance(value, ast.BinOp) and t == PVEC:
            self.unsupported(value, 'expressions on vectors (pvec)', 'use n x 1 matrices (pmat)')
            return
        if isinstance(value, ast.Call):
            vt = self.check_call(value, scope)
            if vt is not None and vt != t:
                self.error(value, 'cannot assign a value of type {} to a variable of type {}'.format(vt, t))
            return
        self.unsupported(value, 'this {} assignment'.format(t))

    # matrix expressions

    def quiet(self, f):
        """f() without its diagnostics."""
        n = len(self.diagnostics)
        result = f()
        del self.diagnostics[n:]
        return result

    def dim(self, node):
        return Dim(eval_dims(node, self.dims_values), node)

    def constructor_shape(self, value):
        if isinstance(value, ast.Call) and len(value.args) == 2:
            return (self.dim(value.args[0]), self.dim(value.args[1]))
        return (UNKNOWN, UNKNOWN)

    def attribute_class(self, node, scope):
        """Class of the object whose attribute node is (no diagnostics)."""
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            return scope.cls
        t = self.quiet(lambda: self.argument_type(node.value, scope))
        return self.classes.get(t.name) if t is not None else None

    def matrix_shape(self, node, scope):
        """Shape of a matrix variable, attribute or List element."""
        if isinstance(node, ast.Name):
            return scope.shapes.get(node.id, (UNKNOWN, UNKNOWN))
        if isinstance(node, ast.Attribute):
            cls = self.attribute_class(node, scope)
            if cls is not None:
                return cls.shapes.get(node.attr, (UNKNOWN, UNKNOWN))
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
            cls = self.attribute_class(node.value, scope)
            sizes = self.dimv_values.get(cls.list_sizes.get(node.value.attr)) if cls else None
            if sizes:
                index = eval_dims(node.slice, self.dims_values)
                if index is not None and 0 <= index < len(sizes):
                    return sizes[index]
                # all the elements have the same size
                if all(s[0] == sizes[0][0] and s[1] == sizes[0][1] for s in sizes):
                    return sizes[0]
        return (UNKNOWN, UNKNOWN)

    def is_matrix(self, node, scope):
        """Whether node is a matrix-valued expression (no diagnostics)."""
        if isinstance(node, ast.Attribute) and node.attr == 'T' and self.is_matrix(node.value, scope):
            return True
        if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            return self.quiet(lambda: self.argument_type(node, scope)) == PMAT
        if isinstance(node, ast.BinOp):
            return isinstance(node.op, ast.MatMult) or self.is_matrix(node.left, scope) or \
                self.is_matrix(node.right, scope)
        if isinstance(node, ast.UnaryOp):
            return self.is_matrix(node.operand, scope)
        if isinstance(node, ast.Call):
            return isinstance(node.func, ast.Name) and node.func.id in MATRIX_FUNCTIONS
        return False

    def is_matrix_expression(self, node, scope):
        """A matrix expression other than a plain matrix (B = A is an alias)."""
        if isinstance(node, ast.Attribute) and node.attr == 'T':
            return self.is_matrix(node, scope)
        if isinstance(node, (ast.BinOp, ast.UnaryOp)):
            return self.is_matrix(node, scope)
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
            node.func.id in MATRIX_FUNCTIONS

    def check_matrix_expression(self, stmt, target, value, scope):
        e = self.matrix_expr(value, scope)
        if e is None:
            return
        shape = self.matrix_shape(target, scope)
        self.check_dim(value, shape[0], e.shape[0], 'the result has {} rows, but {} has {}'.format(
            e.shape[0], ast.unparse(target), shape[0]))
        self.check_dim(value, shape[1], e.shape[1], 'the result has {} columns, but {} has {}'.format(
            e.shape[1], ast.unparse(target), shape[1]))
        plan = Plan(stmt, target, shape, e, position(scope.fun.node))
        try:
            lower_statement(plan, Temporaries(TEMP_PREFIX))
        except LoweringError as err:
            self.error(err.node if err.node is not None else value, err.message)
            return
        self.plans[position(stmt)] = plan

    def check_dim(self, node, a, b, message):
        if a.value is not None and b.value is not None and a.value != b.value:
            self.error(node, 'mismatching sizes: ' + message)
            return False
        return True

    def matrix_expr(self, node, scope):
        """MExpr for a matrix-valued expression, or None (with diagnostics)."""
        if isinstance(node, ast.Attribute) and node.attr == 'T' and self.is_matrix(node.value, scope):
            e = self.matrix_expr(node.value, scope)
            return Transpose(e) if e is not None else None
        if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            if isinstance(node, ast.Subscript) and self.quiet(
                    lambda: self.subscript_base(node.value, scope)) == PMAT:
                self.unsupported(node, 'blocks or elements of matrices in matrix expressions',
                    'copy the block to a matrix first')
                return None
            t = self.argument_type(node, scope)
            if t is None:
                return None
            if t != PMAT:
                self.error(node, "expected a matrix, '{}' is {}".format(ast.unparse(node), t))
                return None
            return Leaf(node, self.matrix_shape(node, scope))
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, (ast.USub, ast.UAdd)):
                self.unsupported(node, "the '{}' operator on matrices".format(op_symbol(node.op)))
                return None
            e = self.matrix_expr(node.operand, scope)
            if e is None or isinstance(node.op, ast.UAdd):
                return e
            return Scale(Coef(-1.0), e)
        if isinstance(node, ast.BinOp):
            return self.matrix_binop(node, scope)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
                node.func.id in MATRIX_FUNCTIONS:
            return self.matrix_call(node, scope)
        if isinstance(node, ast.Call):
            self.unsupported(node, 'calls in matrix expressions (other than {})'.format(
                ', '.join(sorted(MATRIX_FUNCTIONS))), 'assign the result to a matrix first')
            return None
        self.unsupported(node, '{} in matrix expressions'.format(describe(node)))
        return None

    def matrix_binop(self, node, scope):
        op = node.op
        left_m, right_m = self.is_matrix(node.left, scope), self.is_matrix(node.right, scope)
        if isinstance(op, ast.MatMult):
            left, right = self.matrix_expr(node.left, scope), self.matrix_expr(node.right, scope)
            if left is None or right is None:
                return None
            if not self.check_dim(node, left.shape[1], right.shape[0],
                    '({} x {}) @ ({} x {})'.format(*left.shape, *right.shape)):
                return None
            return MatMul(left, right)
        if isinstance(op, (ast.Add, ast.Sub)):
            if not (left_m and right_m):
                self.error(node, "'{}' between a matrix and a number is not supported: "
                    "use pmat_fill for constant matrices".format(op_symbol(op)))
                return None
            left, right = self.matrix_expr(node.left, scope), self.matrix_expr(node.right, scope)
            if left is None or right is None:
                return None
            shapes = '({} x {}) {} ({} x {})'.format(*left.shape, op_symbol(op), *right.shape)
            if not (self.check_dim(node, left.shape[0], right.shape[0], shapes) and
                    self.check_dim(node, left.shape[1], right.shape[1], shapes)):
                return None
            return Add(left, right, 1.0 if isinstance(op, ast.Add) else -1.0)
        if isinstance(op, ast.Mult):
            if left_m and right_m:
                self.error(node, "'*' between matrices is the elementwise product (as in NumPy), "
                    "which is not supported (yet): use '@' for the matrix product")
                return None
            scalar, matrix = (node.right, node.left) if left_m else (node.left, node.right)
            coef = self.scalar_coef(scalar, scope)
            e = self.matrix_expr(matrix, scope)
            if coef is None or e is None:
                return None
            return Scale(coef, e)
        if isinstance(op, ast.Div):
            if right_m:
                self.unsupported(node, 'dividing by a matrix', 'use cho_solve')
                return None
            coef = self.scalar_coef(node.right, scope)
            e = self.matrix_expr(node.left, scope)
            if coef is None or e is None:
                return None
            if not coef.factors:
                return Scale(Coef(1.0 / coef.const), e)
            return Scale(Coef(1.0, [ast.BinOp(left=ast.Constant(1.0), op=ast.Div(),
                right=node.right)]), e)
        self.unsupported(node, "the '{}' operator on matrices".format(op_symbol(op)))
        return None

    def scalar_coef(self, node, scope):
        """A scalar factor of a matrix."""
        literal = node.operand if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) \
            else node
        if isinstance(literal, ast.Constant) and type(literal.value) in (int, float):
            value = float(literal.value)
            return Coef(-value if literal is not node else value)
        self.check_evaluation_order(node, scope)
        t = self.scalar_expr(node, scope)
        if t is None:
            return None
        if t != FLOAT:
            self.error(node, 'a matrix can be multiplied by a float, not by {}'.format(t))
            return None
        return Coef(1.0, [node])

    def matrix_call(self, node, scope):
        name = node.func.id
        if len(node.args) != MATRIX_FUNCTIONS[name] or node.keywords:
            self.error(node, '{} takes {} matrix argument{}'.format(name, MATRIX_FUNCTIONS[name],
                's' if MATRIX_FUNCTIONS[name] > 1 else ''))
            return None
        args = [self.matrix_expr(a, scope) for a in node.args]
        if None in args:
            return None
        square = args[0].shape
        if not self.check_dim(node, square[0], square[1],
                'the first argument of {} must be square, not {} x {}'.format(name, *square)):
            return None
        if name == 'cho_solve':
            if not self.check_dim(node, square[0], args[1].shape[0],
                    'cho_solve(L, B) with L {} x {} and B {} x {}'.format(*square, *args[1].shape)):
                return None
            return Call(name, args, args[1].shape, node)
        return Call(name, args, args[0].shape, node)

    def check_subscript_assignment(self, stmt, target, value, scope):
        base_t = self.subscript_base(target.value, scope)
        if base_t is None:
            return
        if base_t == PMAT:
            indices = matrix_indices(target)
            if indices is None:
                self.error(target, 'a pmat must be indexed with two indices, A[i, j] or A[a:b, c:d]')
                return
            if all(isinstance(i, ast.Slice) for i in indices):
                self.check_slices(indices, scope)
                if isinstance(value, ast.Name):
                    if self.name_type(value, scope) != PMAT:
                        self.error(value, "'{}' is not a pmat".format(value.id))
                elif isinstance(value, ast.Subscript) and \
                        self.subscript_base(value.value, scope) == PMAT:
                    vi = matrix_indices(value)
                    if vi is None or not all(isinstance(i, ast.Slice) for i in vi):
                        self.error(value, 'a block of a matrix must be assigned a matrix or a block A[a:b, c:d]')
                    else:
                        self.check_slices(vi, scope)
                else:
                    self.error(value, 'a block of a matrix must be assigned a matrix or a block A[a:b, c:d]')
                return
            if any(isinstance(i, ast.Slice) for i in indices):
                self.error(target, 'mixing indices and slices is not supported (yet)')
                return
            for i in indices:
                self.index_expr(i, scope)
            self.check_element_value(value, scope)
        elif base_t == PVEC:
            if isinstance(target.slice, (ast.Tuple, ast.Slice)):
                self.error(target, 'a pvec must be indexed with one index, v[i]')
                return
            self.index_expr(target.slice, scope)
            self.check_element_value(value, scope)
        elif is_list(base_t):
            if isinstance(target.slice, (ast.Tuple, ast.Slice)):
                self.error(target, 'a List must be indexed with one index, l[i]')
                return
            self.index_expr(target.slice, scope)
            if base_t.elem == PMAT and self.is_matrix_expression(value, scope):
                self.check_matrix_expression(stmt, target, value, scope)
            elif base_t.elem in (PMAT, PVEC):
                if not isinstance(value, ast.Name) or self.name_type(value, scope) != base_t.elem:
                    self.error(value, 'an element of a List of {} must be assigned a {} variable'.format(
                        base_t.elem, base_t.elem))
            else:
                self.unsupported(target, 'assigning to elements of a List of {}'.format(base_t.elem))
        else:
            self.error(target, 'a value of type {} cannot be indexed'.format(base_t))

    def check_element_value(self, value, scope):
        """Value assigned to a matrix or vector element."""
        if isinstance(value, ast.Constant) and type(value.value) is int:
            return
        self.check_evaluation_order(value, scope)
        vt = self.scalar_expr(value, scope)
        if vt is not None and vt != FLOAT:
            self.error(value, 'matrix and vector elements are float, not {}'.format(vt))

    def check_slices(self, slices, scope):
        for s in slices:
            if s.lower is None or s.upper is None or s.step is not None:
                self.error(s, "slices must have the form 'a:b'")
                continue
            self.index_expr(s.lower, scope)
            self.index_expr(s.upper, scope)

    # expressions

    def name_type(self, node, scope):
        t = scope.lookup(node.id)
        if t is not None:
            return t
        if node.id in scope.loop_vars:
            return INT
        t = self.globals.get(node.id)
        if t is not None:
            return t
        self.error(node, "'{}' is not defined".format(node.id))
        return None

    def scalar_expr(self, node, scope, in_index=False):
        """Type of an arithmetic expression on int and float values. Indices
        (in_index) cannot contain calls and element reads, which are emitted
        as plain text in the generated code."""
        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return INT if type(node.value) is int else FLOAT
            if type(node.value) is bool:
                self.unsupported(node, 'the bool type')
                return None
            self.error(node, 'expected a number, got {}'.format(describe(node)))
            return None
        if isinstance(node, ast.Name):
            t = self.name_type(node, scope)
            if t is None:
                return None
            if t == DIMV or not is_scalar(t):
                self.error(node, "'{}' has type {}, expected a number".format(node.id, t))
                return None
            return t
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ast.USub):
                self.unsupported(node, "the '{}' operator".format(op_symbol(node.op)))
                return None
            return self.scalar_expr(node.operand, scope, in_index)
        if isinstance(node, ast.BinOp):
            left = self.scalar_expr(node.left, scope, in_index)
            right = self.scalar_expr(node.right, scope, in_index)
            if left is None or right is None:
                return None
            if isinstance(node.op, (ast.FloorDiv, ast.Pow)):
                self.unsupported(node, "the '{}' operator".format(op_symbol(node.op)))
                return None
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
                self.unsupported(node, "the '{}' operator".format(op_symbol(node.op)))
                return None
            if is_int_like(left) != is_int_like(right):
                self.error(node, 'mixed int/float arithmetic is not supported: use float literals (e.g. 2.0)')
                return None
            if is_int_like(left):
                if isinstance(node.op, ast.Div):
                    self.error(node, "'/' on integers gives a float in Python but truncates in C: "
                        "use float operands")
                    return None
                if isinstance(node.op, ast.Mod):
                    self.warning(node, "'%' on negative integers gives different results in Python "
                        "and in C")
                return DIMS if left == DIMS and right == DIMS else INT
            if isinstance(node.op, ast.Mod):
                self.error(node, "'%' is not defined on float values")
                return None
            return FLOAT
        if isinstance(node, ast.Call):
            if in_index:
                self.unsupported(node, 'calling a function in an index',
                    'assign the result to a variable first')
                return None
            t = self.check_call(node, scope)
            if t is not None and not is_scalar(t):
                self.error(node, 'expected a number, but this call returns {}'.format(t))
                return None
            return t
        if isinstance(node, ast.Subscript):
            if in_index:
                self.unsupported(node, 'reading an element in an index',
                    'assign it to a variable first')
                return None
            return self.element_read(node, scope)
        if isinstance(node, ast.Attribute):
            t = self.attribute_type(node, scope)
            if t is not None and not is_scalar(t):
                self.error(node, 'expected a number, got an attribute of type {}'.format(t))
                return None
            return t
        self.unsupported(node, describe(node))
        return None

    def check_evaluation_order(self, node, scope):
        """Python evaluates operands from left to right, C in an unspecified
        order: an operand that calls a function with side effects (a method,
        or a function taking a matrix, vector, list or object, which it can
        modify) cannot be combined with operands that read data it could
        modify."""
        if isinstance(node, ast.BinOp):
            operands = [node.left, node.right]
        elif isinstance(node, ast.Compare):
            operands = [node.left] + node.comparators
        elif isinstance(node, ast.Call):
            operands = list(node.args)
        elif isinstance(node, ast.UnaryOp):
            operands = [node.operand]
        elif isinstance(node, ast.BoolOp):
            # and / or are evaluated from left to right in C too
            operands = []
            for value in node.values:
                self.check_evaluation_order(value, scope)
        else:
            operands = []
        if len(operands) > 1:
            effects = [self.has_side_effects(o, scope) for o in operands]
            reads = [any(isinstance(n, (ast.Call, ast.Subscript, ast.Attribute))
                for n in ast.walk(o)) for o in operands]
            for i, effect in enumerate(effects):
                if effect and any(reads[j] for j in range(len(operands)) if j != i):
                    self.error(operands[i], 'this call can modify data read by the rest of the '
                        'expression, which is evaluated in a different order in Python and in C: '
                        'assign its result to a variable first')
                    return
        for o in operands:
            self.check_evaluation_order(o, scope)

    def has_side_effects(self, node, scope):
        for n in ast.walk(node):
            if not isinstance(n, ast.Call) or not isinstance(n.func, (ast.Name, ast.Attribute)):
                continue
            if isinstance(n.func, ast.Attribute) or n.func.id in BUILTINS or \
                    n.func.id in self.casadi_functions:
                return True
            for overload in self.functions.get(n.func.id, []):
                if any(t is not None and not is_scalar(t) for t in overload.arg_types):
                    return True
        return False

    def index_expr(self, node, scope):
        t = self.scalar_expr(node, scope, in_index=True)
        if t is not None and not is_int_like(t):
            self.error(node, 'indices must be integers, not {}'.format(t))

    def check_condition(self, node, scope, top=True):
        """Comparisons, combined with and, or, not."""
        if top:
            self.check_evaluation_order(node, scope)
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                self.check_condition(value, scope, top=False)
            return
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            self.check_condition(node.operand, scope, top=False)
            return
        if not isinstance(node, ast.Compare):
            self.error(node, 'conditions must be comparisons, e.g. a < b')
            return
        operands = [node.left] + node.comparators
        for middle in operands[1:-1]:
            if any(isinstance(n, ast.Call) for n in ast.walk(middle)):
                self.error(middle, 'a call in the middle of a chained comparison would be '
                    'evaluated twice in C: assign its result to a variable first')
                return
        types = [self.scalar_expr(o, scope) for o in operands]
        for op in node.ops:
            if not isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)):
                self.unsupported(node, "the '{}' comparison".format(op_symbol(op)))
                return
        if None in types:
            return
        if len({is_int_like(t) for t in types}) > 1:
            self.error(node, 'comparing int and float values is not supported: use float literals (e.g. 2.0)')

    def element_read(self, node, scope):
        """Value of the element A[i, j], v[i] or l[i]."""
        base_t = self.subscript_base(node.value, scope)
        if base_t is None:
            return None
        if base_t == PMAT:
            indices = matrix_indices(node)
            if indices is None or any(isinstance(i, ast.Slice) for i in indices):
                self.error(node, 'expected an element A[i, j]')
                return None
            for i in indices:
                self.index_expr(i, scope)
            return FLOAT
        if base_t == PVEC:
            self.index_expr(node.slice, scope)
            return FLOAT
        if is_list(base_t):
            self.index_expr(node.slice, scope)
            if base_t.elem in (PMAT, PVEC):
                self.error(node, "'x = l[i]' would make x share its data with the list element: "
                    "use l[i] directly")
                return None
            self.unsupported(node, 'reading elements of a List of {}'.format(base_t.elem))
            return None
        self.error(node, 'a value of type {} cannot be indexed'.format(base_t))
        return None

    def subscript_base(self, node, scope):
        """Type of the indexed value in node[...]."""
        if isinstance(node, ast.Name):
            if node.id in self.globals and scope.lookup(node.id) is None:
                self.error(node, "'{}' is a module-level constant and cannot be indexed".format(node.id))
                return None
            return self.name_type(node, scope)
        if isinstance(node, ast.Attribute):
            return self.attribute_type(node, scope)
        if isinstance(node, ast.Subscript):
            # element of a matrix or vector in a List, e.g. l[k][i, j]
            t = self.subscript_base(node.value, scope)
            if t is None:
                return None
            if not (is_list(t) and t.elem in (PMAT, PVEC)) or \
                    isinstance(node.slice, (ast.Tuple, ast.Slice)):
                self.error(node, 'expected an element of a List of matrices or vectors, l[k]')
                return None
            self.index_expr(node.slice, scope)
            return t.elem
        self.unsupported(node, 'indexing {}'.format(describe(node)))
        return None

    def attribute_type(self, node, scope):
        """Type of obj.attr, self.attr or obj.attr.attr."""
        if isinstance(node.value, ast.Name):
            if node.value.id == 'self':
                if scope.cls is None:
                    self.error(node, "'self' can only be used in methods")
                    return None
                cls = scope.cls
            else:
                t = self.name_type(node.value, scope)
                if t is None:
                    return None
                cls = self.classes.get(t.name)
                if cls is None:
                    self.error(node, "'{}' has type {}, which has no attributes".format(node.value.id, t))
                    return None
        elif isinstance(node.value, ast.Attribute):
            t = self.attribute_type(node.value, scope)
            if t is None:
                return None
            cls = self.classes.get(t.name)
            if cls is None:
                self.error(node, 'a value of type {} has no attributes'.format(t))
                return None
        else:
            self.unsupported(node, 'this attribute access')
            return None
        if node.attr not in cls.attrs:
            self.error(node, "class '{}' has no attribute '{}'".format(cls.name, node.attr))
            return None
        return cls.attrs[node.attr]

    # calls

    def check_expression_statement(self, stmt, scope):
        value = stmt.value
        if not isinstance(value, ast.Call):
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                self.unsupported(stmt, 'docstrings')
            else:
                self.error(stmt, 'this expression has no effect')
            return
        if isinstance(value.func, ast.Name) and value.func.id == 'print':
            self.check_print(value, scope)
            return
        self.check_evaluation_order(value, scope)
        self.check_call(value, scope)

    def check_print(self, node, scope):
        if len(node.args) != 1 or node.keywords:
            self.unsupported(node, 'print with more than one argument',
                "use print('<format>' % value)")
            return
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if re.search(r'%[^%]', arg.value.replace('%%', '')):
                self.error(arg, "this string contains a '%' format but no value")
            return
        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod) and \
                isinstance(arg.left, ast.Constant) and isinstance(arg.left.value, str):
            if isinstance(arg.right, ast.Tuple):
                self.unsupported(arg.right, 'printing more than one value per print')
                return
            specs = re.findall(r'%[-+ #0]*\d*(?:\.\d+)?([a-zA-Z])', arg.left.value.replace('%%', ''))
            if len(specs) != 1:
                self.error(arg.left, 'the format string must contain exactly one %d, %i or %f')
                return
            t = self.scalar_expr(arg.right, scope)
            if t is None:
                return
            if specs[0] in 'di':
                if not is_int_like(t):
                    self.error(arg, "'%{}' expects an int, got {}".format(specs[0], t))
            elif specs[0] in 'feg':
                if t != FLOAT:
                    self.error(arg, "'%{}' expects a float, got {} (the C printf would print "
                        "garbage)".format(specs[0], t))
            else:
                self.unsupported(arg.left, "the '%{}' format".format(specs[0]))
            return
        self.unsupported(node, 'this form of print',
            "use print('<string>') or print('<format>' % value)")

    def check_call(self, node, scope):
        """Check a call and return the type it returns."""
        func = node.func
        allowed = BUILTIN_KEYWORDS.get(func.id, set()) if isinstance(func, ast.Name) else set()
        for kw in node.keywords:
            if kw.arg not in allowed:
                self.unsupported(kw.value if kw.arg is None else kw, 'keyword arguments' if not allowed
                    else "the keyword argument '{}' (accepted: {})".format(kw.arg, ', '.join(sorted(allowed))))
                return None
            literal = kw.value.operand if isinstance(kw.value, ast.UnaryOp) and \
                isinstance(kw.value.op, ast.USub) else kw.value
            if not (isinstance(literal, ast.Constant) and type(literal.value) is float):
                self.error(kw.value, "'{}' must be a float literal, e.g. {}=1.0".format(kw.arg, kw.arg))
                return None
        if isinstance(func, ast.Name):
            name = func.id
            if name in BUILTINS:
                return self.check_builtin_call(node, name, scope)
            if name in UNSUPPORTED_BUILTINS:
                self.unsupported(node, "the built-in function '{}'".format(name))
                return None
            if name in MATH_FUNCTIONS:
                return self.check_math_call(node, name, scope)
            if name in MATRIX_FUNCTIONS:
                self.unsupported(node, '{} outside matrix expressions'.format(name),
                    'assign it to a matrix: L = {}(...)'.format(name))
                return None
            if name in self.casadi_functions:
                return self.check_casadi_call(node, name, scope)
            if name in ('pmat', 'pvec', 'plist') or name in self.classes:
                self.error(node, '{}() can only be used to initialize a declaration'.format(name))
                return None
            if name == 'print':
                self.error(node, 'print cannot be used as a value')
                return None
            if name not in self.functions:
                self.error(node, "function '{}' is not defined".format(name))
                return None
            if name == 'main':
                self.error(node, 'main cannot be called')
                return None
            return self.check_overloaded_call(node, self.functions[name], scope)
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id == 'self':
                cls = scope.cls
                if cls is None:
                    self.error(node, "'self' can only be used in methods")
                    return None
            else:
                if isinstance(func.value, ast.Name):
                    t = self.name_type(func.value, scope)
                else:
                    t = self.attribute_type(func.value, scope) \
                        if isinstance(func.value, ast.Attribute) else None
                if t is None:
                    if not isinstance(func.value, (ast.Name, ast.Attribute)):
                        self.unsupported(node, 'this method call')
                    return None
                cls = self.classes.get(t.name)
                if cls is None:
                    self.error(node, 'a value of type {} has no methods'.format(t))
                    return None
            if func.attr not in cls.methods or func.attr == '__init__':
                self.error(node, "class '{}' has no method '{}'".format(cls.name, func.attr))
                return None
            return self.check_overloaded_call(node, cls.methods[func.attr], scope)
        self.unsupported(node, 'this kind of call')
        return None

    def check_casadi_call(self, node, name, scope):
        n_in, n_out = self.casadi_functions[name]
        if len(node.args) != n_in + n_out:
            self.error(node, 'CasADi function {} takes {} inputs and {} outputs (matrices that '
                'it writes), {} arguments given'.format(name, n_in, n_out, len(node.args)))
            return None
        for arg in node.args:
            t = self.argument_type(arg, scope)
            if t is not None and t != PMAT:
                self.error(arg, 'the arguments of CasADi functions must be matrices (pmat), '
                    'not {}'.format(t))
                return None
        return NONE

    def check_math_call(self, node, name, scope):
        arity = MATH_FUNCTIONS[name]
        if len(node.args) != arity:
            self.error(node, '{} takes {} argument{}'.format(name, arity, 's' if arity > 1 else ''))
            return None
        types = [self.scalar_expr(a, scope) for a in node.args]
        if None in types:
            return None
        if name in ('abs', 'min', 'max'):
            if DIMS in types:
                self.unsupported(node, '{} of dims constants'.format(name),
                    'assign the value to an int variable first')
                return None
            if len(set(types)) > 1:
                self.error(node, 'the arguments of {} must be both int or both float'.format(name))
                return None
            return types[0]
        if types[0] != FLOAT:
            self.error(node, '{} takes a float argument, not {} (use e.g. 2.0)'.format(name, types[0]))
            return None
        return FLOAT

    def check_builtin_call(self, node, name, scope):
        arg_types = [self.argument_type(a, scope) for a in node.args]
        if None in arg_types:
            return None
        for params, ret in BUILTINS[name]:
            if len(params) == len(arg_types) and all(
                    argument_matches(a, p) for a, p in zip(arg_types, params)):
                self.check_output_aliasing(node, name)
                return ret
        self.error(node, '{}({}) does not match {}'.format(name, ', '.join(map(str, arg_types)),
            ' or '.join('{}({})'.format(name, ', '.join(map(str, p))) for p, r in BUILTINS[name])))
        return None

    def check_output_aliasing(self, node, name):
        if name not in OUTPUT_ALIASING:
            return
        out, inputs = OUTPUT_ALIASING[name]
        out_arg = node.args[out]
        for i in inputs:
            if ast.dump(node.args[i]) == ast.dump(out_arg):
                self.error(out_arg, "the output of {} must be a different matrix than its "
                    "input '{}': it cannot be computed in place".format(name, ast.unparse(node.args[i])))
                return

    def check_overloaded_call(self, node, overloads, scope):
        arg_types = [self.argument_type(a, scope) for a in node.args]
        if None in arg_types:
            return None
        for fun in overloads:
            if len(fun.arg_types) == len(arg_types) and all(
                    p is not None and argument_matches(a, p) for a, p in zip(arg_types, fun.arg_types)):
                return fun.ret_type
        self.error(node, "no definition of '{}' takes ({})".format(overloads[0].name,
            ', '.join(map(str, arg_types))))
        return None

    def argument_type(self, node, scope):
        if isinstance(node, ast.Name):
            return self.name_type(node, scope)
        if isinstance(node, ast.Subscript):
            base_t = self.subscript_base(node.value, scope)
            if base_t is None:
                return None
            if is_list(base_t) and base_t.elem in (PMAT, PVEC):
                self.index_expr(node.slice, scope)
                return base_t.elem
            if base_t == PMAT and any(isinstance(i, ast.Slice) for i in
                    (node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice])):
                self.unsupported(node, 'passing a block of a matrix as an argument',
                    'copy it to a matrix first')
                return None
            return self.element_read(node, scope)
        if isinstance(node, ast.Attribute):
            t = self.attribute_type(node, scope)
            if t is not None and is_list(t):
                self.unsupported(node, 'passing a List attribute as an argument')
                return None
            return t
        if isinstance(node, ast.Call):
            return self.check_call(node, scope)
        return self.scalar_expr(node, scope)

    # control flow

    def check_for(self, stmt, scope):
        if stmt.orelse:
            self.unsupported(stmt, "'else' on loops")
        if not isinstance(stmt.target, ast.Name):
            self.error(stmt.target, 'the loop variable must be a name')
            return
        name = stmt.target.id
        self.check_identifier(stmt.target, name)
        if scope.lookup(name) is not None:
            self.error(stmt.target, "loop variable '{}' shadows a declared variable".format(name))
            return
        if name in scope.loop_vars:
            self.warning(stmt.target, "nested loops reuse the loop variable '{}': after the inner "
                "loop, its value differs in Python and in C".format(name))
        it = stmt.iter
        if not (isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id == 'range'):
            self.unsupported(it, 'iterating over anything but range(...)')
            return
        if not 1 <= len(it.args) <= 3 or it.keywords:
            self.error(it, 'range takes 1 to 3 arguments')
            return
        for arg in it.args[:2]:
            self.index_expr(arg, scope)
        if len(it.args) == 3:
            step = it.args[2]
            literal = step.operand if isinstance(step, ast.UnaryOp) and \
                isinstance(step.op, ast.USub) else step
            if not (isinstance(literal, ast.Constant) and type(literal.value) is int and literal.value):
                self.unsupported(step, 'a range step that is not a non-zero integer literal')
                return
        scope.loop_vars.append(name)
        scope.push()
        scope.loops += 1
        self.check_block(stmt.body, scope)
        scope.loops -= 1
        scope.pop()
        scope.loop_vars.pop()

    def check_return(self, stmt, scope):
        ret = scope.fun.ret_type
        if ret is None:
            return
        value = stmt.value
        is_none = value is None or (isinstance(value, ast.Constant) and value.value is None)
        if ret == NONE:
            if not is_none:
                self.error(stmt, "function '{}' returns None".format(scope.fun.name))
            return
        if is_none:
            self.error(stmt, "function '{}' must return a {}".format(scope.fun.name, ret))
            return
        if ret in (PMAT, PVEC):
            if not isinstance(value, ast.Name) or self.name_type(value, scope) != ret:
                self.error(value, 'expected a {} variable'.format(ret))
            return
        self.check_evaluation_order(value, scope)
        vt = self.scalar_expr(value, scope)
        if vt is not None and not same_scalar(vt, ret) and not (
                isinstance(value, ast.Constant) and type(value.value) is int and ret == FLOAT):
            self.error(value, "function '{}' must return a {}, not {}".format(scope.fun.name, ret, vt))


# helpers

def matrix_indices(node):
    if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 2:
        return node.slice.elts
    return None


def same_scalar(a, b):
    return a == b or (is_int_like(a) and is_int_like(b))


def argument_matches(arg, param):
    if is_list(param) and is_list(arg):
        return param.elem is None or param.elem == arg.elem
    return same_scalar(arg, param) if is_scalar(arg) and is_scalar(param) else arg == param


def ends_with_return(body):
    if not body:
        return False
    last = body[-1]
    if isinstance(last, ast.Return):
        return True
    if isinstance(last, ast.If):
        return ends_with_return(last.body) and ends_with_return(last.orelse)
    return False


def describe(node):
    names = {
        'AugAssign': 'augmented assignment', 'Break': "'break'", 'Continue': "'continue'",
        'Pass': "'pass'", 'Try': "'try'", 'With': "'with'", 'Raise': "'raise'",
        'Assert': "'assert'", 'Delete': "'del'", 'Global': "'global'", 'Nonlocal': "'nonlocal'",
        'Lambda': 'lambda', 'ListComp': 'list comprehensions', 'DictComp': 'dict comprehensions',
        'SetComp': 'set comprehensions', 'GeneratorExp': 'generator expressions',
        'Dict': 'dicts', 'Set': 'sets', 'Tuple': 'tuples', 'List': 'lists',
        'JoinedStr': 'f-strings', 'IfExp': 'conditional expressions', 'Yield': "'yield'",
        'Await': "'await'", 'AsyncFunctionDef': 'async functions', 'Match': "'match'",
        'Starred': 'starred expressions', 'NamedExpr': "':='", 'Expr': 'expression statements',
        'If': "'if'", 'For': "'for'", 'While': "'while'", 'Assign': 'assignments',
        'Return': "'return'", 'FunctionDef': 'nested functions', 'ClassDef': 'nested classes',
    }
    return names.get(type(node).__name__, type(node).__name__)


def op_symbol(op):
    return {
        ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: '//',
        ast.Mod: '%', ast.Pow: '**', ast.MatMult: '@', ast.BitAnd: '&', ast.BitOr: '|',
        ast.BitXor: '^', ast.LShift: '<<', ast.RShift: '>>', ast.Not: 'not',
        ast.Invert: '~', ast.UAdd: '+', ast.USub: '-', ast.Lt: '<', ast.LtE: '<=',
        ast.Gt: '>', ast.GtE: '>=', ast.Eq: '==', ast.NotEq: '!=', ast.Is: 'is',
        ast.IsNot: 'is not', ast.In: 'in', ast.NotIn: 'not in',
    }.get(type(op), type(op).__name__)


def analyze(tree, casadi_functions=None):
    """Check a prometeo program; return the list of diagnostics and the
    assignments of matrix expressions to lower (see matexpr.lower).

    casadi_functions: CasADi functions defined in pure blocks, as a dict
    name -> (number of inputs, number of outputs)."""
    checker = Checker(casadi_functions)
    checker.check_module(normalize(deepcopy(tree)))
    unique = {(d.lineno, d.col, d.severity, d.message): d for d in checker.diagnostics}
    return sorted(unique.values(), key=lambda d: (d.lineno, d.col)), checker.plans


def check(tree, casadi_functions=None):
    """Check a prometeo program; return the list of diagnostics."""
    return analyze(tree, casadi_functions)[0]
