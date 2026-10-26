"""Random matrix expressions (prometeo/frontend/matexpr.py), checked against
NumPy.

Each generated program assigns random expressions (+, -, scalar factors, @,
.T, cholesky, cho_solve, blocks A[a:b, c:d], targets read by their
expression, +=) to matrices and blocks of matrices of different shapes and
prints the results. The program must print the same
numbers in Python and as transpiled C, and these must match the same
expressions evaluated with NumPy, which has the same syntax. Set
PMT_RANDOM_EXPRESSIONS=<count> to test more programs, PMT_RANDOM_SEED=<seed>
to start from another seed.
"""

import ast
import os
import random

import numpy as np
import pytest
import scipy.linalg

from prometeo.frontend import check

from pmt_testing import run_pmt, assert_same_numbers, extract_numbers

COUNT = int(os.environ.get('PMT_RANDOM_EXPRESSIONS', '10'))
FIRST_SEED = int(os.environ.get('PMT_RANDOM_SEED', '0'))

DIMS = {'n': 3, 'm': 2}


class ExpressionProgram:

    def __init__(self, seed):
        self.rng = random.Random(seed)
        rng = self.rng
        # matrices: name -> (rows, cols) as dims names
        self.mats = {}
        shapes = [(r, c) for r in DIMS for c in DIMS]
        # at least one matrix of each shape
        for i in range(7):
            self.mats['X{}'.format(i)] = shapes[i] if i < len(shapes) else rng.choice(shapes)
        # a larger matrix, for blocks
        self.big = {'W': 5}
        # well-conditioned lower triangular factors, for cho_solve
        self.factors = {'Ln': 'n', 'Lm': 'm'}
        self.scalars = {'s0': round(rng.uniform(-2, 2), 2), 's1': round(rng.uniform(-2, 2), 2)}
        self.init = []
        for name, (r, c) in self.mats.items():
            for i in range(DIMS[r]):
                for j in range(DIMS[c]):
                    self.init.append('{}[{}, {}] = {}'.format(name, i, j, self.literal()))
        for name, size in self.big.items():
            for i in range(size):
                for j in range(size):
                    self.init.append('{}[{}, {}] = {}'.format(name, i, j, self.literal()))
        for name, d in self.factors.items():
            for i in range(DIMS[d]):
                for j in range(i + 1):
                    value = round(rng.uniform(1.0, 2.0), 2) if i == j else self.literal()
                    self.init.append('{}[{}, {}] = {}'.format(name, i, j, value))

    def literal(self):
        return '{:.2f}'.format(self.rng.uniform(-1.0, 1.0))

    def size_of(self, name):
        if name in self.big:
            return (self.big[name], self.big[name])
        r, c = self.mats[name]
        return (DIMS[r], DIMS[c])

    def block(self, r, c):
        """A random block A[a:b, c:d] of r x c (dims names) elements."""
        rng = self.rng
        rows, cols = DIMS[r], DIMS[c]
        name = rng.choice([n for n in list(self.mats) + list(self.big)
            if self.size_of(n)[0] >= rows and self.size_of(n)[1] >= cols])
        slices = []
        for size, total, dim in ((rows, self.size_of(name)[0], r), (cols, self.size_of(name)[1], c)):
            start = rng.randint(0, total - size)
            form = rng.choice(['literal', 'dims', 'open'])
            if start == 0 and size == total and form == 'open':
                slices.append(':')
            elif start + size == total and form == 'open':
                slices.append('{}:'.format(start))
            elif start == 0 and form == 'open':
                slices.append(':{}'.format(size))
            elif form == 'dims':
                slices.append('{}:{} + {}'.format(start, start, dim))
            else:
                slices.append('{}:{}'.format(start, start + size))
        return '{}[{}, {}]'.format(name, *slices)

    def expr(self, r, c, depth):
        """A random expression of shape (r, c)."""
        rng = self.rng
        leaves = [n for n, s in self.mats.items() if s == (r, c)]
        tleaves = [n + '.T' for n, s in self.mats.items() if s == (c, r)]
        if depth <= 0 or rng.random() < 0.25:
            if rng.random() < 0.3:
                return self.block(r, c) if rng.random() < 0.7 else self.block(c, r) + '.T'
            return rng.choice(leaves + tleaves)
        kind = rng.choice(['add', 'sub', 'scale', 'scalevar', 'div', 'neg', 'matmul', 'matmul',
            'transpose', 'cholesky', 'cho_solve'])
        d = depth - 1
        if kind in ('add', 'sub'):
            return '{} {} {}'.format(self.expr(r, c, d), '+' if kind == 'add' else '-', self.term(r, c, d))
        if kind == 'scale':
            return '{} * {}'.format(self.literal(), self.term(r, c, d))
        if kind == 'scalevar':
            return '{} * {}'.format(rng.choice(sorted(self.scalars)), self.term(r, c, d))
        if kind == 'div':
            return '{} / {}'.format(self.term(r, c, d), rng.choice(['2.0', '4.0']))
        if kind == 'neg':
            return '-{}'.format(self.term(r, c, d))
        if kind == 'transpose':
            return '({}).T'.format(self.expr(c, r, d))
        if kind == 'cholesky' and r == c:
            # cholesky of a symmetric positive definite matrix
            L, t = 'L' + r, self.term(r, r, 0)
            return 'cholesky({} @ {}.T + {} @ {}.T)'.format(L, L, t, t)
        if kind == 'cho_solve':
            return 'cho_solve(L{}, {})'.format(r, self.expr(r, c, d))
        k = rng.choice(list(DIMS))
        return '{} @ {}'.format(self.term(r, k, d), self.term(k, c, d))

    def term(self, r, c, depth):
        e = self.expr(r, c, depth)
        atomic = isinstance(ast.parse(e, mode='eval').body,
            (ast.Name, ast.Attribute, ast.Call, ast.Subscript))
        return e if atomic else '(' + e + ')'

    def statements(self, count):
        rng = self.rng
        stmts = []
        for _ in range(count):
            target = rng.choice(sorted(self.mats))
            r, c = self.mats[target]
            base = target
            if rng.random() < 0.3:
                # a block as target
                r, c = rng.choice(list(DIMS)), rng.choice(list(DIMS))
                target = self.block(r, c)
                base = target.split('[')[0]
            e = self.expr(r, c, rng.randint(1, 3))
            if base == target and isinstance(ast.parse(e, mode='eval').body, (ast.Name, ast.Subscript)):
                # B = A is an alias (B = A[...] a view), not an expression
                e = '-' + e
            if rng.random() < 0.3:
                # the target in the expression
                e = '{} - 0.5 * {}'.format(target, self.term(r, c, 1)) if rng.random() < 0.5 \
                    else '{} @ {}'.format(self.term(r, c, 1), target) if r == c \
                    else '{} + {}'.format(e, target)
            op = '+=' if rng.random() < 0.15 else '='
            stmts.append((target, op, e, base))
        return stmts

    def source(self, stmts):
        lines = ['from prometeo import *', '']
        lines += ['{} : dims = {}'.format(k, v) for k, v in DIMS.items()]
        lines += ['', 'def main() -> int:']
        for name, (r, c) in self.mats.items():
            lines.append('    {} : pmat = pmat({}, {})'.format(name, r, c))
        for name, size in self.big.items():
            lines.append('    {} : pmat = pmat({}, {})'.format(name, size, size))
        for name, d in self.factors.items():
            lines.append('    {} : pmat = pmat({}, {})'.format(name, d, d))
        for name, value in self.scalars.items():
            lines.append('    {} : float = {}'.format(name, value))
        lines += ['    ' + l for l in self.init]
        for target, op, e, base in stmts:
            lines.append('    {} {} {}'.format(target, op, e))
            r, c = self.size_of(base)
            lines.append('    for i in range({}):'.format(r))
            lines.append('        for j in range({}):'.format(c))
            lines.append("            print('%.15e\\n' % {}[i, j])".format(base))
        lines += ['    return 0', '']
        return '\n'.join(lines)

    def numpy_results(self, stmts):
        env = {'cholesky': np.linalg.cholesky,
            'cho_solve': lambda L, B: scipy.linalg.cho_solve((L, True), B)}
        env.update(self.scalars)
        env.update(DIMS)
        for name, (r, c) in self.mats.items():
            env[name] = np.zeros((DIMS[r], DIMS[c]))
        for name, size in self.big.items():
            env[name] = np.zeros((size, size))
        for name, d in self.factors.items():
            env[name] = np.zeros((DIMS[d], DIMS[d]))
        for line in self.init:
            exec(line, env)
        results = []
        for target, op, e, base in stmts:
            exec('{} {} {}'.format(target, op, e), env)
            # prometeo writes into the target: no views (e.g. of X.T) in NumPy
            env[base] = np.array(env[base])
            results += list(env[base].flatten())
        return results


@pytest.mark.parametrize('seed', range(FIRST_SEED, FIRST_SEED + COUNT))
def test_random_matrix_expressions(seed, tmp_path):
    program = ExpressionProgram(seed)
    stmts = program.statements(8)
    source = program.source(stmts)
    (tmp_path / 'program.py').write_text(source)
    errors = [d for d in check(ast.parse(source)) if d.severity == 'error']
    assert not errors, 'generated program rejected: {}\n{}'.format(errors, source)
    py_code, py_output = run_pmt(str(tmp_path), 'program.py', cgen=False)
    assert py_code == 0, py_output + source
    c_code, c_output = run_pmt(str(tmp_path), 'program.py', cgen=True)
    assert c_code == 0, c_output + source
    assert_same_numbers(py_output, c_output)
    got = np.array(extract_numbers(py_output))
    expected = np.array(program.numpy_results(stmts))
    assert got.shape == expected.shape, source
    scale = max(1.0, np.abs(expected).max())
    assert np.abs(got - expected).max() <= 1e-10 * scale, source
