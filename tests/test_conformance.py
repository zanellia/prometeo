"""Conformance tests for the prometeo language (docs/source/language/language.rst).

Each case in tests/conformance/*.txt is a small program with its expected
outcome:

    ### <name>
    # expect: ok                     accepted; Python and C print the same
    # expect: warning <message>      same as ok, with a warning
    # expect: error <message>        rejected by the checker
    <body of main(), indented by 4 spaces>
    @<module-level line>             (lines starting with '@')

Every program gets 'from prometeo import *' and 'n : dims = 3'.
"""

import ast
import glob
import os
import re

import pytest

from prometeo.cmdline.pmt import normalize_plist_types, strip_pure_blocks
from prometeo.frontend import check

from pmt_testing import run_pmt, assert_same_numbers

CASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conformance')


def load_cases():
    cases = []
    for path in sorted(glob.glob(os.path.join(CASES_DIR, '*.txt'))):
        topic = os.path.splitext(os.path.basename(path))[0]
        blocks = re.split(r'^### (.*)$', open(path).read(), flags=re.M)[1:]
        for name, body in zip(blocks[::2], blocks[1::2]):
            lines = body.strip('\n').splitlines()
            expect = re.match(r'# expect: (ok|warning|error)\s*(.*)$', lines[0])
            assert expect, 'missing "# expect:" line in case {} of {}'.format(name, path)
            module = [l[1:] for l in lines[1:] if l.startswith('@')]
            main = [l for l in lines[1:] if not l.startswith('@') and l.strip()]
            source = 'from prometeo import *\n\nn : dims = 3\n\n' + '\n'.join(module) + \
                '\n\ndef main() -> int:\n' + '\n'.join(main) + '\n    return 0\n'
            cases.append(pytest.param(source, expect.group(1), expect.group(2),
                id='{}::{}'.format(topic, name.strip())))
    return cases


CASES = load_cases()


@pytest.mark.parametrize('source, expect, message', CASES)
def test_checker(source, expect, message):
    diagnostics = check(normalize_plist_types(ast.parse(strip_pure_blocks(source))))
    errors = [d.message for d in diagnostics if d.severity == 'error']
    warnings = [d.message for d in diagnostics if d.severity == 'warning']
    if expect == 'error':
        assert any(message in e for e in errors), (message, errors)
    else:
        assert not errors, errors
        if expect == 'warning':
            assert any(message in w for w in warnings), (message, warnings)


@pytest.mark.parametrize('source, expect, message',
    [c for c in CASES if c.values[1] != 'error'])
def test_accepted_program_runs_identically(source, expect, message, tmp_path):
    (tmp_path / 'program.py').write_text(source)
    py_code, py_output = run_pmt(str(tmp_path), 'program.py', cgen=False)
    assert py_code == 0, py_output
    c_code, c_output = run_pmt(str(tmp_path), 'program.py', cgen=True)
    assert c_code == 0, c_output
    assert_same_numbers(py_output, c_output)


def test_rejected_program_exits_with_error(tmp_path):
    (tmp_path / 'program.py').write_text(
        'from prometeo import *\n\ndef main() -> int:\n    k = 1\n    return 0\n')
    for cgen in (False, True):
        code, output = run_pmt(str(tmp_path), 'program.py', cgen=cgen)
        assert code == 1, output
        assert "'k' must be declared before it is assigned" in output, output
