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
    ('    x : pmat = pmat(n, 1)\n    y : pmat = pmat(1, 1)\n    J : pmat = pmat(n, n)\n'
        '    k : int = 1\n    f(x, y, x, J, k)\n',
        'the arguments of CasADi functions must be matrices (pmat) or vectors (pvec), not int'),
    ('    x : pmat = pmat(n, 1)\n    y : pmat = pmat(1, 1)\n    J : pmat = pmat(n, n)\n'
        '    t : float = 0.0\n    t = f(x, y, x, J, y)\n',
        'expected a number, but this call returns None'),
    ('    x : pmat = pmat(n, 1)\n    y : pmat = pmat(1, 1)\n    J : pmat = pmat(n, 1)\n'
        '    f(x, y, x, J, y)\n',
        'CasADi function f: output 1 has size 3 x 1, expected 3 x 3'),
    ('    x : pvec = pvec(n)\n    y : pmat = pmat(1, 1)\n    J : pvec = pvec(n)\n'
        '    f(x, y, x, J, y)\n',
        'CasADi function f: output 1 is a 3x3 matrix, not a vector'),
    ('    x : pvec = pvec(2)\n    y : pmat = pmat(1, 1)\n    J : pmat = pmat(n, n)\n'
        '    f(x, y, x, J, y)\n',
        'CasADi function f: input 0 has size 2, expected 3'),
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
    # the sizes of function arguments are not known at compile time
    source = program('''\
    x : pmat = pmat(n, 1)
    y : pmat = pmat(1, 1)
    z : pmat = pmat(n, 1)
    J : pmat = pmat(n, 1)
    s : pmat = pmat(1, 1)
    call_f(x, y, z, J, s)
''').replace('def main', 'def call_f(x: pmat, y: pmat, z: pmat, J: pmat, s: pmat) -> None:\n'
        '    f(x, y, z, J, s)\n    return\n\ndef main')
    (tmp_path / 'program.py').write_text(source)
    (py_code, py_out), (c_code, c_out) = [run_pmt(str(tmp_path), 'program.py', cgen=cgen)
        for cgen in (False, True)]
    assert py_code != 0 and 'output 1 has size 3x1, expected 3x3' in py_out, py_out
    assert c_code != 0 and 'out_1 has size 3x1, expected 3x3' in c_out, c_out


def test_vector_arguments(tmp_path):
    # column vectors can be passed as vectors, in any combination with matrices
    (py_code, py_out), (c_code, c_out) = run_both(tmp_path, program('''\
    x : pvec = pvec(n)
    xm : pmat = pmat(n, 1)
    y : pmat = pmat(1, 1)
    z : pvec = pvec(n)
    zm : pmat = pmat(n, 1)
    J : pmat = pmat(n, n)
    s : pmat = pmat(1, 1)
    x[0] = 0.3
    x[1] = -1.2
    x[2] = 0.7
    xm[0, 0] = 0.3
    xm[1, 0] = -1.2
    xm[2, 0] = 0.7
    y[0, 0] = 2.0
    f(x, y, z, J, s)
    pvec_print(z)
    f(xm, y, zm, J, s)
    pmat_print(zm)
    f(x, y, zm, J, s)
    pmat_print(zm)
    f(xm, y, z, J, s)
    pvec_print(z)
    pmat_print(J)
    # z = f(x) - x
    f(x, y, z, J, s)
    z = z - x
    pvec_print(z)
'''))
    assert py_code == 0, py_out
    assert c_code == 0, c_out
    assert_same_numbers(py_out, c_out)
    # the same numbers with vectors and matrices
    from pmt_testing import extract_numbers
    numbers = extract_numbers(py_out)
    assert numbers[0:3] == numbers[3:6] == numbers[6:9] == numbers[9:12], py_out
