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
import subprocess
import sys

import pytest

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
    ('riccati_example', 'riccati', True),
    # the pure-Python block (numpy) only runs in the interpreter
    ('pure_python_inline', 'pure_python_inline', False),
    # the interpreted run takes too long
    ('fibonacci', 'fibonacci', False),
    # the interpreted run fails (method called with a missing argument)
    ('simple_class', 'simple_class', False),
]

NUMBER = re.compile(r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|[-+]?nan|[-+]?inf')
IGNORED_LINE = re.compile(r'prometeo|execution time|total time|Execution time|bytes aligned')


def run_pmt(workdir, name, cgen):
    cmd = [sys.executable, '-m', 'prometeo', name + '.py', '--cgen={}'.format(cgen)]
    proc = subprocess.run(cmd, cwd=workdir, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
    assert proc.returncode == 0, proc.stdout
    return proc.stdout


def extract_numbers(output):
    numbers = []
    for line in output.splitlines():
        if IGNORED_LINE.search(line):
            continue
        numbers += [float(x) for x in NUMBER.findall(line)]
    return numbers


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
    c_output = run_pmt(workdir, name, cgen=True)

    cache = os.path.join(workdir, '__pmt_cache__')
    for ext in ('c', 'h'):
        with open(os.path.join(cache, name + '.' + ext)) as f:
            check_golden(name + '.' + ext, f.read())
    check_golden(name + '.heap', heap_sizes(os.path.join(cache, 'Makefile')))

    c_numbers = extract_numbers(c_output)
    assert not any(math.isnan(x) for x in c_numbers), c_output

    if differential:
        py_numbers = extract_numbers(run_pmt(workdir, name, cgen=False))
        assert len(c_numbers) == len(py_numbers), (c_output, py_numbers)
        for c, py in zip(c_numbers, py_numbers):
            assert math.isclose(c, py, rel_tol=1e-6, abs_tol=1e-9), (c_output, py_numbers)
