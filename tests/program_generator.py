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
        self.floats = ['x{}'.format(k) for k in range(rng.randint(2, 4))]
        self.ints = ['k{}'.format(k) for k in range(rng.randint(1, 3))]
        self.counters = ['c{}'.format(k) for k in range(2)]
        self.functions = []
        self.lines = []
        self.loop_depth = 0
        self.statements = 0

    # expressions

    def float_literal(self):
        return '{:.2f}'.format(self.rng.choice([-1, 1]) * self.rng.uniform(0.1, 2.0))

    def float_expr(self, depth=2):
        rng = self.rng
        if depth == 0 or rng.random() < 0.3:
            return rng.choice(self.floats) if rng.random() < 0.6 else self.float_literal()
        op = rng.choice(['+', '-', '*', '/', 'neg'])
        if op == 'neg':
            return '-' + self.float_expr(depth - 1)
        if op == '/':
            # divide by a literal far from 0
            return '({}) / {}'.format(self.float_expr(depth - 1), rng.choice(['2.0', '4.0', '-0.5']))
        return '({} {} {})'.format(self.float_expr(depth - 1), op, self.float_expr(depth - 1))

    def int_const_expr(self, depth=2):
        """Integer expression of literals and dims constants."""
        rng = self.rng
        if depth == 0 or rng.random() < 0.4:
            return rng.choice(list(self.dims)) if rng.random() < 0.4 else str(rng.randint(-3, 5))
        return '({} {} {})'.format(self.int_const_expr(depth - 1), rng.choice(['+', '-', '*']),
            self.int_const_expr(depth - 1))

    def index(self, dim, loop_var=None):
        """Index in range(dim): a literal, a loop variable or dim - 1 - i."""
        size = self.dims[dim]
        if loop_var is not None and self.rng.random() < 0.7:
            return loop_var if self.rng.random() < 0.6 else '{} - 1 - {}'.format(dim, loop_var)
        return str(self.rng.randint(0, size - 1))

    def matrix(self, shape=None):
        names = [m for m, s in self.matrices.items() if shape is None or s == shape]
        return self.rng.choice(names) if names else None

    def condition(self):
        rng = self.rng
        if rng.random() < 0.5:
            return '{} {} {}'.format(rng.choice(self.floats), rng.choice(['<', '>', '<=', '>=']),
                self.float_literal())
        return '{} {} {}'.format(rng.choice(self.ints), rng.choice(['<', '>', '==', '!=']),
            rng.randint(-3, 5))

    # statements

    def emit(self, indent, line):
        self.lines.append('    ' * indent + line)

    def block(self, indent, count):
        for _ in range(count):
            self.statement(indent)

    def statement(self, indent):
        self.statements += 1
        rng = self.rng
        kinds = ['float', 'float', 'int', 'el_write', 'el_read', 'builtin', 'builtin', 'operator',
            'print']
        if indent < 3 and self.statements < self.max_statements:
            kinds += ['for', 'if', 'while']
        if self.functions:
            kinds.append('call')
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
            a = self.matrix()
            r, c = self.matrices[a]
            self.emit(indent, '{}[{}, {}] = {}'.format(a, self.index(r), self.index(c),
                rng.choice(self.floats + [self.float_literal()])))
        elif kind == 'el_read':
            a = self.matrix()
            r, c = self.matrices[a]
            self.emit(indent, '{} = {}[{}, {}]'.format(rng.choice(self.floats), a,
                self.index(r), self.index(c)))
        elif kind == 'builtin':
            self.builtin(indent)
        elif kind == 'operator':
            self.operator(indent)
        elif kind == 'print':
            if rng.random() < 0.5:
                self.emit(indent, "print('%f\\n' % {})".format(rng.choice(self.floats)))
            else:
                self.emit(indent, 'pmat_print({})'.format(self.matrix()))
        elif kind == 'for':
            self.loop(indent)
        elif kind == 'if':
            self.emit(indent, 'if {}:'.format(self.condition()))
            self.block(indent + 1, rng.randint(1, 3))
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
            self.block(indent + 1, rng.randint(1, 3))
            self.emit(indent + 1, '{} = {} + 1'.format(c, c))
            self.active_counters.remove(c)
        elif kind == 'call':
            name, shape = rng.choice(self.functions)
            self.emit(indent, '{} = {}({}, {})'.format(rng.choice(self.floats), name,
                self.matrix(shape), rng.choice(self.floats)))

    def loop(self, indent):
        rng = self.rng
        a = self.matrix()
        r, c = self.matrices[a]
        i = 'i{}'.format(self.loop_depth)
        self.emit(indent, 'for {} in range({}):'.format(i, r))
        self.loop_depth += 1
        if rng.random() < 0.5:
            j = 'i{}'.format(self.loop_depth)
            self.emit(indent + 1, 'for {} in range({}):'.format(j, c))
            self.emit(indent + 2, '{}[{}, {}] = {}'.format(a, self.index(r, i), self.index(c, j),
                rng.choice(self.floats + [self.float_literal()])))
        else:
            self.emit(indent + 1, '{}[{}, {}] = {}'.format(a, self.index(r, i), self.index(c),
                rng.choice(self.floats + [self.float_literal()])))
            if rng.random() < 0.5:
                self.emit(indent + 1, '{} = {}[{}, {}]'.format(rng.choice(self.floats), a,
                    self.index(r, i), self.index(c)))
        self.loop_depth -= 1

    def builtin(self, indent):
        rng = self.rng
        kind = rng.choice(['copy', 'tran', 'gemm', 'gead', 'fill'])
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
        else:
            self.emit(indent, 'pmat_fill({}, {})'.format(self.matrix(), self.float_literal()))

    def operator(self, indent):
        rng = self.rng
        op = rng.choice(['*', '+', '-'])
        a = self.matrix()
        r, k = self.matrices[a]
        if op == '*':
            b = self.matrix((k, rng.choice(['n', 'm'])))
            if b is None:
                return self.builtin(indent)
            target_shape = (r, self.matrices[b][1])
        else:
            b = self.matrix((r, k))
            target_shape = (r, k)
        # the result must be a different matrix than the operands
        targets = [m for m, s in self.matrices.items() if s == target_shape and m not in (a, b)]
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
            '    y : float = 0.0',
            '    y = A[{}, {}]'.format(self.rng.randint(0, self.dims[r] - 1),
                self.rng.randint(0, self.dims[c] - 1)),
            '    A[{}, {}] = x'.format(self.rng.randint(0, self.dims[r] - 1),
                self.rng.randint(0, self.dims[c] - 1)),
            '    return y * {} + x'.format(self.float_literal()),
            '',
        ]
        self.functions.append((name, shape))
        return lines

    def generate(self):
        rng = self.rng
        header = ['from prometeo import *', '']
        header += ['{} : dims = {}'.format(d, v) for d, v in self.dims.items()]
        header.append('')
        functions = []
        for k in range(rng.randint(0, 2)):
            functions += self.function(k)
        self.active_counters = []
        self.emit(1, '# declarations')
        for a, (r, c) in self.matrices.items():
            self.emit(1, '{} : pmat = pmat({}, {})'.format(a, r, c))
        for x in self.floats:
            self.emit(1, '{} : float = {}'.format(x, self.float_literal()))
        for k in self.ints:
            self.emit(1, '{} : int = {}'.format(k, rng.randint(-3, 5)))
        for c in self.counters:
            self.emit(1, '{} : int = 0'.format(c))
        # start from non-zero matrices
        for a, (r, c) in self.matrices.items():
            self.emit(1, 'for i in range({}):'.format(r))
            self.emit(2, 'for j in range({}):'.format(c))
            self.emit(3, '{}[i, j] = {}'.format(a, self.float_literal()))
        self.emit(1, '# random statements')
        while self.statements < self.max_statements:
            self.statement(1)
        self.emit(1, '# results')
        for x in self.floats:
            self.emit(1, "print('%f\\n' % {})".format(x))
        for k in self.ints:
            self.emit(1, "print('%i\\n' % {})".format(k))
        for a in self.matrices:
            self.emit(1, 'pmat_print({})'.format(a))
        self.emit(1, 'return 0')
        return '\n'.join(header + functions + ['def main() -> int:'] + self.lines) + '\n'


def generate(seed, max_statements=40):
    return ProgramGenerator(seed, max_statements).generate()


if __name__ == '__main__':
    import sys
    print(generate(int(sys.argv[1]) if len(sys.argv) > 1 else 0))
