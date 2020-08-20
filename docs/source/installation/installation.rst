Installation
============

PyPI installation
*****************

prometeo can be installed through PyPI with `pip install prometeo-dsl`. Notice that, since prometeo makes extensive use of `type hints <https://docs.python.org/3.6/library/typing.html>`__ to equip Python code with static typing information, the minimum Python version required is 3.6.

manual installation
*******************

If you want to install prometeo building the sources on your local machine you can proceed as follows:

- Run `git submodule update --init` to clone the submodules.
- Run `make install_shared` from `<prometeo_root>/prometeo/cpmt` to compile and install the shared library associated with the C backend. Notice that the default installation path is `<prometeo_root>/prometeo/cpmt/install`.
- You need Python 3.6. or later.
- Optional: to keep things clean you can setup a virtual environment with `virtualenv --python=<path_to_python3.6> <path_to_new_virtualenv>`.
- Run `pip install -e .` from `<prometeo_root>` to install the Python package.

Finally, you can run the examples in `<root>/examples` with `pmt <example_name>.py --cgen=<True/False>`, where the `--cgen` flag determines whether the code is executed by the Python interpreter or C code is generated compiled and run.
