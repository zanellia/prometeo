"""Differential testing on random programs (tests/program_generator.py).

Every generated program must be accepted by the checker and print the same
numbers in Python and as transpiled C. Set PMT_RANDOM_PROGRAMS=<count> to
test more programs, and PMT_RANDOM_SEED=<seed> to start from another seed.
"""

import ast
import os

import pytest

from prometeo.frontend import check

from pmt_testing import run_pmt, assert_same_numbers
from program_generator import generate

COUNT = int(os.environ.get('PMT_RANDOM_PROGRAMS', '20'))
FIRST_SEED = int(os.environ.get('PMT_RANDOM_SEED', '0'))


@pytest.mark.parametrize('seed', range(FIRST_SEED, FIRST_SEED + COUNT))
def test_random_program(seed, tmp_path):
    source = generate(seed)
    (tmp_path / 'program.py').write_text(source)
    errors = [d for d in check(ast.parse(source)) if d.severity == 'error']
    assert not errors, 'generated program rejected: {}\n{}'.format(errors, source)
    py_code, py_output = run_pmt(str(tmp_path), 'program.py', cgen=False)
    assert py_code == 0, py_output
    c_code, c_output = run_pmt(str(tmp_path), 'program.py', cgen=True)
    assert c_code == 0, c_output
    assert_same_numbers(py_output, c_output)
