"""prometeo command line tool"""

import sys
from prometeo.cmdline import pmt_main

def console_entry() -> None:
    return pmt_main()

if __name__ == '__main__':
    pmt_main()
