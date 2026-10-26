"""Random generator of valid prometeo programs, for differential testing.

Programs only use constructs accepted by the checker; running one in Python
and as transpiled C must print the same numbers.
"""

import random


class ProgramGenerator:

    def __init__(self, seed, max_statements=40):
        self.rng = random.Random(seed)
        self.max_statements = max_statements
        rng = self.rng
        self.dims = {'n': rng.randint(2, 4), 'm': rng.randint(2, 4)}
        shapes = [('n', 'n'), ('n', 'm'), ('m', 'n'), ('m', 'm')]
        self.matrices = {}
        for k in range(rng.randint(3, 5)):
            self.matrices['A{}'.format(k)] = rng.choice(shapes)
        # make sure there are square matrices and transposable pairs
        self.matrices['S0'] = ('n', 'n')
        self.matrices['T0'] = ('m', 'n')
        self.vectors = {'V0': 'n', 'V1': 'm'}
        self.floats = ['x{}'.format(k) for k in range(rng.randint(2, 4))]
        self.ints = ['k{}'.format(k) for k in range(rng.randint(1, 3))]
        self.counters = ['c{}'.format(k) for k in range(2)]
        # functions that modify their matrix argument, and pure scalar functions
        self.functions = []
        self.pure_functions = []
        self.lines = []
        # enclosing loops: (loop variable or None for while loops, dims name)
        self.loops = []
        self.statements = 0

    # expressions

    def float_literal(self):
        return '{:.2f}'.format(self.rng.choice([-1, 1]) * self.rng.uniform(0.1, 2.0))

    def loop_var(self, dim):
        """A loop variable ranging over range(dim), if any."""
        candidates = [v for v, d in self.loops if v is not None and d == dim]
        return self.rng.choice(candidates) if candidates else None

    def index(self, dim):
        """Index in range(dim): a literal, a loop variable or dim - 1 - i."""
        var = self.loop_var(dim)
        if var is not None and self.rng.random() < 0.7:
            return var if self.rng.random() < 0.6 else '{} - 1 - {}'.format(dim, var)
        return str(self.rng.randint(0, self.dims[dim] - 1))

    def math_call(self):
        """Math function with a bounded result."""
        rng = self.rng
        arg = self.float_expr(1)
        kind = rng.choice(['sin', 'cos', 'exp', 'sqrt', 'abs', 'min', 'max', 'tanh'])
        if kind == 'exp':
            return 'exp(-abs({}))'.format(arg)
        if kind == 'sqrt':
            return 'sqrt(abs({}))'.format(arg)
        if kind in ('min', 'max'):
            return '{}({}, {})'.format(kind, arg, self.float_leaf())
        if kind == 'tanh':
            # log and exp: log(1 + exp(-|x|)) is bounded
            return 'log(1.0 + exp(-abs({})))'.format(arg)
        return '{}({})'.format(kind, arg)

    def element(self):
        if self.rng.random() < 0.15:
            # element of a vector in a List attribute
            return 'acc.hist[{}][{}, 0]'.format(self.rng.randint(0, 2), self.index('n'))
        if self.rng.random() < 0.75:
            a = self.matrix()
            r, c = self.matrices[a]
            return '{}[{}, {}]'.format(a, self.index(r), self.index(c))
        v = self.rng.choice(list(self.vectors))
        return '{}[{}]'.format(v, self.index(self.vectors[v]))

    def float_leaf(self):
        r = self.rng.random()
        if r < 0.35:
            return self.rng.choice(self.floats)
        if r < 0.5:
            return self.element()
        if r < 0.6:
            return self.math_call()
        if r < 0.7:
            return 'acc.total'
        if r < 0.8 and self.pure_functions:
            return '{}({})'.format(self.rng.choice(self.pure_functions), self.float_expr(1))
        return self.float_literal()

    def float_expr(self, depth=2):
        """Float expression without side effects."""
        rng = self.rng
        if depth == 0 or rng.random() < 0.3:
            return self.float_leaf()
        op = rng.choice(['+', '-', '*', '/', 'neg'])
        if op == 'neg':
            return '-' + self.float_expr(depth - 1)
        if op == '/':
            # divide by a literal far from 0
            return '({}) / {}'.format(self.float_expr(depth - 1), rng.choice(['2.0', '4.0', '-0.5']))
        return '({} {} {})'.format(self.float_expr(depth - 1), op, self.float_expr(depth - 1))

    def int_const_expr(self, depth=2):
        """Integer expression of literals, dims constants and loop variables."""
        rng = self.rng
        if depth == 0 or rng.random() < 0.4:
            r = rng.random()
            loop_vars = [v for v, d in self.loops if v is not None]
            if r < 0.3 and loop_vars:
                return rng.choice(loop_vars)
            if r < 0.4:
                return '{}({}, {})'.format(rng.choice(['min', 'max']), str(rng.randint(-3, 5)),
                    rng.choice(self.ints))
            return rng.choice(list(self.dims)) if r < 0.6 else str(rng.randint(-3, 5))
        return '({} {} {})'.format(self.int_const_expr(depth - 1), rng.choice(['+', '-', '*']),
            self.int_const_expr(depth - 1))

    def matrix(self, shape=None):
        names = [m for m, s in self.matrices.items() if shape is None or s == shape]
        return self.rng.choice(names) if names else None

    def comparison(self):
        rng = self.rng
        r = rng.random()
        if r < 0.4:
            return '{} {} {}'.format(self.float_expr(1), rng.choice(['<', '>', '<=', '>=']),
                self.float_literal())
        if r < 0.55:
            low, high = sorted([self.float_literal(), self.float_literal()], key=float)
            return '{} < {} < {}'.format(low, rng.choice(self.floats), high)
        return '{} {} {}'.format(rng.choice(self.ints + [v for v, d in self.loops if v]),
            rng.choice(['<', '>', '==', '!=']), rng.randint(-3, 5))

    def condition(self, depth=1):
        rng = self.rng
        r = rng.random()
        if depth == 0 or r < 0.5:
            return self.comparison()
        if r < 0.65:
            return 'not {}'.format(self.comparison())
        return '({} {} {})'.format(self.condition(depth - 1), rng.choice(['and', 'or']),
            self.condition(depth - 1))

    # statements

    def emit(self, indent, line):
        self.lines.append('    ' * indent + line)

    def block(self, indent, count):
        for _ in range(count):
            self.statement(indent)

    def statement(self, indent):
        self.statements += 1
        rng = self.rng
        kinds = ['float', 'float', 'int', 'el_write', 'el_write', 'aug', 'builtin', 'builtin',
            'operator', 'print', 'method']
        if indent < 4 and self.statements < self.max_statements:
            kinds += ['for', 'if', 'while']
        if self.functions:
            kinds.append('call')
        if self.loops:
            kinds.append('jump')
        kind = rng.choice(kinds)
        if kind == 'float':
            self.emit(indent, '{} = {}'.format(rng.choice(self.floats), self.float_expr()))
        elif kind == 'int':
            # at most one variable plus a constant: values grow at most linearly
            # in loops (C ints overflow, Python ints do not)
            const = self.int_const_expr()
            if rng.random() < 0.7:
                const = '{} {} {}'.format(rng.choice(self.ints), rng.choice(['+', '-']), const)
            self.emit(indent, '{} = {}'.format(rng.choice(self.ints), const))
        elif kind == 'el_write':
            self.emit(indent, '{} = {}'.format(self.element(), self.float_expr(1)))
        elif kind == 'aug':
            r = rng.random()
            if r < 0.4:
                self.emit(indent, '{} {}= {}'.format(rng.choice(self.floats), rng.choice('+-*'),
                    self.float_expr(1)))
            elif r < 0.8:
                # '*=' on elements could grow without bound in loops
                self.emit(indent, '{} {}= {}'.format(self.element(), rng.choice('+-'),
                    self.float_expr(1)))
            else:
                self.emit(indent, '{} {}= {}'.format(rng.choice(self.ints), rng.choice('+-'),
                    self.int_const_expr(1)))
        elif kind == 'builtin':
            self.builtin(indent)
        elif kind == 'operator':
            self.operator(indent)
        elif kind == 'print':
            r = rng.random()
            if r < 0.4:
                self.emit(indent, "print('%f\\n' % ({}))".format(self.float_expr(1)))
            elif r < 0.6:
                self.emit(indent, "print('%i\\n' % ({}))".format(self.int_const_expr(1)))
            elif r < 0.8:
                self.emit(indent, 'pmat_print({})'.format(self.matrix()))
            else:
                self.emit(indent, 'pvec_print({})'.format(rng.choice(list(self.vectors))))
        elif kind == 'method':
            r = rng.random()
            if r < 0.4:
                self.emit(indent, 'acc.add({})'.format(self.float_expr(1)))
            elif r < 0.6:
                self.emit(indent, 'acc.bump()')
            else:
                self.emit(indent, '{} = acc.get()'.format(rng.choice(self.floats)))
        elif kind == 'for':
            self.loop(indent)
        elif kind == 'if':
            self.emit(indent, 'if {}:'.format(self.condition()))
            self.block(indent + 1, rng.randint(1, 3))
            if rng.random() < 0.3:
                self.emit(indent, 'elif {}:'.format(self.condition()))
                self.block(indent + 1, rng.randint(1, 2))
            if rng.random() < 0.5:
                self.emit(indent, 'else:')
                self.block(indent + 1, rng.randint(1, 3))
        elif kind == 'while':
            counters = [c for c in self.counters if c not in self.active_counters]
            if not counters:
                return self.statement(indent)
            c = counters[0]
            self.active_counters.append(c)
            self.emit(indent, '{} = 0'.format(c))
            self.emit(indent, 'while {} < {}:'.format(c, rng.randint(1, 3)))
            # the counter is incremented first: 'continue' cannot skip it
            self.emit(indent + 1, '{} += 1'.format(c))
            self.loops.append((None, None))
            self.block(indent + 1, rng.randint(1, 3))
            self.loops.pop()
            self.active_counters.remove(c)
        elif kind == 'jump':
            self.emit(indent, 'if {}:'.format(self.condition()))
            self.emit(indent + 1, rng.choice(['break', 'continue']))
        elif kind == 'call':
            name, shape = rng.choice(self.functions)
            self.emit(indent, '{} = {}({}, {})'.format(rng.choice(self.floats), name,
                self.matrix(shape), self.float_expr(1)))

    def loop(self, indent):
        rng = self.rng
        i = 'i{}'.format(len(self.loops))
        dim = rng.choice(list(self.dims))
        r = rng.random()
        if r < 0.6:
            iterator = 'range({})'.format(dim)
        elif r < 0.8:
            iterator = 'range({} - 1, -1, -1)'.format(dim)
        else:
            iterator = 'range(0, {}, 2)'.format(dim)
        self.emit(indent, 'for {} in {}:'.format(i, iterator))
        self.loops.append((i, dim))
        self.block(indent + 1, rng.randint(1, 3))
        self.loops.pop()

    def builtin(self, indent):
        rng = self.rng
        kind = rng.choice(['copy', 'tran', 'gemm', 'gead', 'fill', 'attr'])
        if kind == 'copy':
            a = self.matrix()
            b = self.matrix(self.matrices[a])
            self.emit(indent, 'pmat_copy({}, {})'.format(a, b))
        elif kind == 'tran':
            a = self.matrix()
            r, c = self.matrices[a]
            targets = [m for m, s in self.matrices.items() if s == (c, r) and m != a]
            if not targets:
                return self.builtin(indent)
            self.emit(indent, 'pmat_tran({}, {})'.format(a, rng.choice(targets)))
        elif kind == 'gemm':
            a = self.matrix()
            r, k = self.matrices[a]
            b = self.matrix((k, rng.choice(['n', 'm'])))
            if b is None:
                return self.builtin(indent)
            c = self.matrix((r, self.matrices[b][1]))
            if c is None or c in (a, b):
                return self.builtin(indent)
            self.emit(indent, 'pmt_gemm_nn({}, {}, {}, {})'.format(a, b, c, c))
        elif kind == 'gead':
            a = self.matrix()
            b = self.matrix(self.matrices[a])
            self.emit(indent, 'pmt_gead({}, {}, {})'.format(self.float_literal(), a, b))
        elif kind == 'fill':
            self.emit(indent, 'pmat_fill({}, {})'.format(self.matrix(), self.float_literal()))
        else:
            # matrix attribute as an argument
            s = self.matrix(('n', 'n'))
            if rng.random() < 0.5:
                self.emit(indent, 'pmat_copy({}, acc.M)'.format(s))
            else:
                self.emit(indent, 'pmat_copy(acc.M, {})'.format(s))

    def operator(self, indent):
        rng = self.rng
        op = rng.choice(['@', '+', '-'])
        a = self.matrix()
        r, k = self.matrices[a]
        if op == '@':
            b = self.matrix((k, rng.choice(['n', 'm'])))
            if b is None:
                return self.builtin(indent)
            target_shape = (r, self.matrices[b][1])
        else:
            b = self.matrix((r, k))
            target_shape = (r, k)
        # the target can also be an operand (computed through a temporary)
        targets = [m for m, s in self.matrices.items() if s == target_shape]
        if not targets:
            return self.builtin(indent)
        self.emit(indent, '{} = {} {} {}'.format(rng.choice(targets), a, op, b))

    # program

    def function(self, k):
        shape = self.rng.choice(list(set(self.matrices.values())))
        name = 'f{}'.format(k)
        r, c = shape
        lines = [
            'def {}(A: pmat, x: float) -> float:'.format(name),
            '    y : float = A[{}, {}]'.format(self.rng.randint(0, self.dims[r] - 1),
                self.rng.randint(0, self.dims[c] - 1)),
            '    A[{}, {}] += x'.format(self.rng.randint(0, self.dims[r] - 1),
                self.rng.randint(0, self.dims[c] - 1)),
            '    return y * {} + x'.format(self.float_literal()),
            '',
        ]
        self.functions.append((name, shape))
        return lines

    def pure_function(self, k):
        name = 'g{}'.format(k)
        self.pure_functions.append(name)
        return [
            'def {}(x: float) -> float:'.format(name),
            '    if x > {}:'.format(self.float_literal()),
            '        return x * {}'.format(self.float_literal()),
            '    return x - {}'.format(self.float_literal()),
            '',
        ]

    def accumulator_class(self):
        return [
            'class Acc:',
            '    def __init__(self) -> None:',
            '        self.total : float = 0.0',
            '        self.count : int = 0',
            '        self.M : pmat = pmat(n, n)',
            '        self.hist : List = plist(pmat, hist_sizes)',
            '',
            '    def add(self, x: float) -> None:',
            '        self.total += x',
            '        self.count += 1',
            '        self.M[0, 0] = self.M[0, 0] + x',
            '        return',
            '',
            '    def get(self) -> float:',
            '        return self.total * 0.5 + self.M[0, 0]',
            '',
            '    def bump(self) -> None:',
            '        # methods calling methods; shift the history',
            '        self.add(0.25)',
            '        pmat_copy(self.hist[1], self.hist[2])',
            '        pmat_copy(self.hist[0], self.hist[1])',
            '        self.hist[0][0, 0] = self.get()',
            '        return',
            '',
        ]

    def generate(self):
        rng = self.rng
        header = ['from prometeo import *', '']
        header += ['{} : dims = {}'.format(d, v) for d, v in self.dims.items()]
        header.append('hist_sizes : dimv = [[n, 1]] * 3')
        header.append('')
        functions = self.accumulator_class()
        for k in range(rng.randint(0, 2)):
            functions += self.function(k)
        for k in range(rng.randint(0, 2)):
            functions += self.pure_function(k)
        self.active_counters = []
        self.emit(1, '# declarations')
        self.emit(1, 'acc : Acc = Acc()')
        for a, (r, c) in self.matrices.items():
            self.emit(1, '{} : pmat = pmat({}, {})'.format(a, r, c))
        for v, d in self.vectors.items():
            self.emit(1, '{} : pvec = pvec({})'.format(v, d))
        for x in self.floats:
            self.emit(1, '{} : float = {}'.format(x, self.float_literal()))
        for k in self.ints:
            self.emit(1, '{} : int = {}'.format(k, rng.randint(-3, 5)))
        for c in self.counters:
            self.emit(1, '{} : int = 0'.format(c))
        # start from non-zero matrices and vectors
        for a, (r, c) in self.matrices.items():
            self.emit(1, 'for i in range({}):'.format(r))
            self.emit(2, 'for j in range({}):'.format(c))
            self.emit(3, '{}[i, j] = {}'.format(a, self.float_literal()))
        for v, d in self.vectors.items():
            self.emit(1, 'for i in range({}):'.format(d))
            self.emit(2, '{}[i] = {}'.format(v, self.float_literal()))
        self.emit(1, '# random statements')
        while self.statements < self.max_statements:
            self.statement(1)
        self.emit(1, '# results')
        for x in self.floats:
            self.emit(1, "print('%f\\n' % {})".format(x))
        for k in self.ints:
            self.emit(1, "print('%i\\n' % {})".format(k))
        self.emit(1, "print('%f\\n' % acc.total)")
        self.emit(1, "print('%i\\n' % acc.count)")
        for a in self.matrices:
            self.emit(1, 'pmat_print({})'.format(a))
        for v in self.vectors:
            self.emit(1, 'pvec_print({})'.format(v))
        self.emit(1, 'pmat_print(acc.M)')
        for j in range(3):
            self.emit(1, 'pmat_print(acc.hist[{}])'.format(j))
        self.emit(1, 'return 0')
        return '\n'.join(header + functions + ['def main() -> int:'] + self.lines) + '\n'


def generate(seed, max_statements=40):
    return ProgramGenerator(seed, max_statements).generate()


if __name__ == '__main__':
    import sys
    print(generate(int(sys.argv[1]) if len(sys.argv) > 1 else 0))
