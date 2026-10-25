"""CasADi functions defined in pure blocks and called from prometeo code."""

import pytest

from pmt_testing import run_pmt, assert_same_numbers

HEADER = '''from prometeo import *

n : dims = 3

# pure >
import casadi as ca
x = ca.SX.sym('x', n)
y = ca.SX.sym('y', 1, 1)
# a sparse Jacobian: the outputs are densified
z = ca.vertcat(ca.sin(x[0]) * y, x[1] * x[2], ca.exp(-x[2]))
f = casadi_function(ca.Function('f', [x, y], [z, ca.jacobian(z, x), ca.sumsqr(x)]))
# pure <

'''


def program(main_body):
    return HEADER + 'def main() -> int:\n' + main_body + '    return 0\n'


def run_both(tmp_path, source):
    (tmp_path / 'program.py').write_text(source)
    return [run_pmt(str(tmp_path), 'program.py', cgen=cgen) for cgen in (False, True)]


def test_outputs_match(tmp_path):
    (py_code, py_out), (c_code, c_out) = run_both(tmp_path, program('''\
    x : pmat = pmat(n, 1)
    y : pmat = pmat(1, 1)
    z : pmat = pmat(n, 1)
    J : pmat = pmat(n, n)
    s : pmat = pmat(1, 1)
    x[0, 0] = 0.3
    x[1, 0] = -1.2
    x[2, 0] = 0.7
    y[0, 0] = 2.0
    f(x, y, z, J, s)
    pmat_print(z)
    pmat_print(J)
    pmat_print(s)
    # inputs and outputs can be the same matrix
    f(x, y, x, J, s)
    pmat_print(x)
'''))
    assert py_code == 0, py_out
    assert c_code == 0, c_out
    assert_same_numbers(py_out, c_out)


@pytest.mark.parametrize('body, message', [
    ('    x : pmat = pmat(n, 1)\n    f(x, x)\n', 'CasADi function f takes 2 inputs and 3 outputs'),
    ('    x : pmat = pmat(n, 1)\n    k : int = 1\n    f(x, x, x, x, k)\n',
        'the arguments of CasADi functions must be matrices'),
    ('    x : pmat = pmat(n, 1)\n    t : float = 0.0\n    t = f(x, x, x, x, x)\n',
        'expected a number, but this call returns None'),
])
def test_checker_errors(tmp_path, body, message):
    for code, output in run_both(tmp_path, program(body)):
        assert code == 1, output
        assert message in output, output


def test_redefinition(tmp_path):
    # a prometeo function f, then replaced by the CasADi function f
    source = program('    print("ok\\n")\n').replace(
        'n : dims = 3\n', 'n : dims = 3\n\ndef f(a: int) -> int:\n    return a\n')
    for code, output in run_both(tmp_path, source):
        assert code == 1, output
        assert "'f' is a CasADi function and cannot be redefined" in output, output


def test_wrong_size_at_run_time(tmp_path):
    (py_code, py_out), (c_code, c_out) = run_both(tmp_path, program('''\
    x : pmat = pmat(n, 1)
    y : pmat = pmat(1, 1)
    z : pmat = pmat(n, 1)
    J : pmat = pmat(n, 1)
    s : pmat = pmat(1, 1)
    f(x, y, z, J, s)
'''))
    assert py_code != 0 and 'output 1 has size 3x1, expected 3x3' in py_out, py_out
    assert c_code != 0 and 'out_1 has size 3x1, expected 3x3' in c_out, c_out
