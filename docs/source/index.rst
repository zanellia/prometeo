.. prometeo documentation master file, created by
   sphinx-quickstart on Tue Aug 18 13:58:41 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to prometeo's documentation!
====================================
This is prometeo, an experimental modeling tool for embedded high-performance computing. prometeo provides a domain specific language (DSL) based on a subset of the Python language that allows one to conveniently write scientific computing programs in a high-level language (Python itself) that can be transpiled to high-performance self-contained C code easily deployable on embedded devices.

features
--------

1. **Python compatible syntax :** prometeo is a DSL embedded into the Python language. prometeo programs can be executed from the Python interpreter.

2. **efficient :** prometeo programs transpile to high-performance C code.
3. **statically typed :** prometeo uses Python's native type hints to strictly enforce static typing.
4. **deterministic memory usage :** a specific program structure is required and enforced through static analysis. In this way prometeo transpiled programs have a guaranteed maximum heap usage.
5. **fast memory menagement :** thanks to its static analysis, prometeo can avoid allocating and garbage-collecting memory, resulting in faster and safer execution.
6. **self-contained and embeddable :** unlike other similar tools and languages, prometeo targets specifically embedded applications and programs written in prometeo transpile to self-contained C code that does not require linking against the Python run-time library.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   installation/installation
   python_syntax/python_syntax
   blas_api/blas_api
   performance/performance

