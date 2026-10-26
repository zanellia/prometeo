Installation
============

prometeo needs Python 3.10 or later (it is tested with 3.10 to 3.14), a C
compiler and make.

PyPI installation
*****************

Releases are published on PyPI: ``pip install prometeo-dsl``. The features
described in this documentation may be more recent than the latest release:
to use them, install from source.

Installation from source
************************

.. code-block:: bash

    git clone https://github.com/zanellia/prometeo.git
    cd prometeo
    git submodule update --init                     # BLASFEO
    make -C prometeo/cpmt install_shared            # BLASFEO and the C runtime, into prometeo/lib
    python3 -m venv .venv && source .venv/bin/activate
    pip install -e .

Then run the examples in ``examples/`` with ``pmt <example>.py`` (in Python)
or ``pmt <example>.py --cgen=True`` (transpiled to C, compiled and run).

BLASFEO is built for ``X64_INTEL_HASWELL`` (x86-64 with AVX2) by default. For
other CPUs, choose its target, e.g. ``make -C prometeo/cpmt install_shared
TARGET=GENERIC`` (any CPU; the tests and CI use it) or
``TARGET=ARMV8A_ARM_CORTEX_A57``; the targets are listed in
``external/blasfeo/Makefile.rule``. On larger problems the target matters:
the AVX2 kernels are several times faster than the generic ones.

Tests
*****

.. code-block:: bash

    pip install -e '.[test]'
    pytest tests
