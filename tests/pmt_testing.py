"""Helpers shared by the tests: run prometeo programs and compare outputs."""

import math
import os
import re
import subprocess
import sys

NUMBER = re.compile(r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|[-+]?nan|[-+]?inf')
IGNORED_LINE = re.compile(r'prometeo|execution time|total time|Execution time|bytes aligned')


def run_pmt(workdir, filename, cgen, check=True):
    """Run `pmt <filename> --cgen=<cgen>` in workdir; return (exit code, output)."""
    cmd = [sys.executable, '-m', 'prometeo', filename, '--cgen={}'.format(cgen),
        '--check={}'.format(check)]
    # allocate exactly the computed heap bound, so that the runtime check in
    # the generated code catches any program that needs more
    env = dict(os.environ)
    env.setdefault('PMT_HEAP_MARGIN', '1')
    proc = subprocess.run(cmd, cwd=workdir, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, universal_newlines=True, timeout=600)
    return proc.returncode, proc.stdout


# diagnostics of the C compiler (e.g. clang's warnings, with the lines they
# refer to): not printed by the program
COMPILER_LINE = re.compile(r'^\S+\.[ch]:\d+:\d+: (warning|error|note):|^\s*\d* \||'
    r'^\d+ warnings? (and \d+ errors? )?generated')


def extract_numbers(output):
    """The numbers printed by a program run by pmt (not by the compiler)."""
    numbers = []
    for line in output.splitlines():
        if IGNORED_LINE.search(line) or COMPILER_LINE.search(line):
            continue
        numbers += [float(x) for x in NUMBER.findall(line)]
    return numbers


def assert_same_numbers(py_output, c_output):
    py_numbers = extract_numbers(py_output)
    c_numbers = extract_numbers(c_output)
    assert not any(math.isnan(x) for x in c_numbers), c_output
    assert len(c_numbers) == len(py_numbers), (py_output, c_output)
    for c, py in zip(c_numbers, py_numbers):
        assert math.isclose(c, py, rel_tol=1e-6, abs_tol=1e-9), (py_output, c_output)
