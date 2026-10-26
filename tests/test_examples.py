"""End-to-end tests over the examples.

For every example we check:
  * golden: the generated C code (.c, .h) and the computed heap sizes match
    the reference files in tests/golden/ (regenerate them with
    PMT_UPDATE_GOLDEN=1 pytest tests/ and review the diff);
  * differential: the numbers printed by the transpiled C program match the
    ones printed when running the same program in the Python interpreter.
"""

import math
import os
import re
import shutil

import pytest

from pmt_testing import run_pmt, extract_numbers, assert_same_numbers

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(ROOT, 'examples')
GOLDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'golden')
UPDATE_GOLDEN = os.environ.get('PMT_UPDATE_GOLDEN', '0') == '1'

# (example directory, program name, run differential test)
EXAMPLES = [
    ('helloworld', 'helloworld', True),
    ('simple_example', 'simple_example', True),
    ('test', 'test', True),
    ('test', 'test_assignments', True),
    ('test', 'test_forward_call', True),
    ('test', 'test_lapack', True),
    ('riccati_example', 'riccati', True),
    # SQP for MPC (cart-pole), also checked against IPOPT in test_sqp_reference.py
    ('sqp_mpc', 'sqp_mpc', True),
    # the same, written with matrix expressions
    ('sqp_mpc', 'sqp_mpc_hl', True),
    # the same SQP on a hanging chain of masses (21 states)
    ('sqp_mpc', 'chain_mpc', True),
    # README benchmark: the interpreted run (10000 repetitions) takes too long
    ('riccati_example', 'riccati_mass_spring', False),
    ('riccati_example', 'riccati_mass_spring_2', True),
    ('riccati_example', 'riccati_debug', True),
    # prints nothing
    ('riccati_example', 'riccati_array', False),
    # the pure-Python block (numpy) only runs in the interpreter
    ('pure_python_inline', 'pure_python_inline', False),
    # the interpreted run takes too long
    ('fibonacci', 'fibonacci', False),
    # the interpreted run fails (method called with a missing argument)
    ('simple_class', 'simple_class', False),
]

def heap_sizes(makefile):
    with open(makefile) as f:
        sizes = re.findall(r'^(HEAP\d+_SIZE = \d+)$', f.read(), re.MULTILINE)
    return '\n'.join(sizes) + '\n'


def check_golden(golden_name, actual):
    golden_file = os.path.join(GOLDEN_DIR, golden_name)
    if UPDATE_GOLDEN:
        os.makedirs(GOLDEN_DIR, exist_ok=True)
        with open(golden_file, 'w') as f:
            f.write(actual)
        return
    assert os.path.exists(golden_file), \
        'missing golden file {} (run with PMT_UPDATE_GOLDEN=1)'.format(golden_file)
    with open(golden_file) as f:
        expected = f.read()
    assert actual == expected, 'generated output differs from {}'.format(golden_file)


@pytest.fixture
def workdir(tmp_path, request):
    example_dir = request.param
    dest = tmp_path / example_dir
    shutil.copytree(os.path.join(EXAMPLES_DIR, example_dir), str(dest),
        ignore=shutil.ignore_patterns('__pmt_cache__'))
    return str(dest)


@pytest.mark.parametrize('workdir, name, differential',
    EXAMPLES, indirect=['workdir'], ids=[e[1] for e in EXAMPLES])
def test_example(workdir, name, differential):
    code, c_output = run_pmt(workdir, name + '.py', cgen=True)
    assert code == 0, c_output

    cache = os.path.join(workdir, '__pmt_cache__')
    for ext in ('c', 'h'):
        with open(os.path.join(cache, name + '.' + ext)) as f:
            check_golden(name + '.' + ext, f.read())
    check_golden(name + '.heap', heap_sizes(os.path.join(cache, 'Makefile')))

    assert not any(math.isnan(x) for x in extract_numbers(c_output)), c_output

    if differential:
        code, py_output = run_pmt(workdir, name + '.py', cgen=False)
        assert code == 0, py_output
        assert_same_numbers(py_output, c_output)
