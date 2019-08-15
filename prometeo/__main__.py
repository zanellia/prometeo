"""prometeo command line tool"""

import sys
from prometeo.cmdline import pmt_main

def console_entry() -> None:
    pmt_main(None, sys.stdout, sys.stderr)

if __name__ == '__main__':
    pmt_main(None, sys.stdout, sys.stderr)
