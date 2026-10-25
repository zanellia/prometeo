Language reference
==================

prometeo programs are Python programs written in a restricted subset of the
language. A program can be run by the Python interpreter (``pmt program.py``)
or transpiled to C, compiled and run (``pmt program.py --cgen=True``); both
must give the same results.

Before running or transpiling, ``pmt`` checks the program against the rules
on this page and reports every violation with its source location::

     > prometeo: error at program.py:8:9: matrices, vectors, lists and objects
       must be declared outside loops and conditionals: ...
             A : pmat = pmat(n, n)
             ^

Rules marked *(not supported yet)* are limitations of the current
implementation; the others are part of the language, usually because the
construct would behave differently in Python and in C. Each rule is covered by
a test case in ``tests/conformance``.

The check can be disabled with ``--check=False`` to try experimental features
(e.g. CasADi functions), with no guarantees.

Program structure
-----------------

A program consists of, in this order of appearance (functions and classes can
be referenced before their definition):

- the import ``from prometeo import *``; other imports are only allowed in
  pure Python blocks (see below);
- module-level constants;
- functions and classes;
- a function ``def main() -> int``, which must end with ``return 0``.

Module-level constants must be declared with a type and initialized with a
constant expression of literals, previously declared constants, ``+``, ``-``
and ``*``:

.. code-block:: python

    n : dims = 4                      # integer constant usable as a size
    m : dims = 2 * n
    sizes : dimv = [[n, n], [n, m]]   # [rows, cols] pairs, to size a List of matrices
    nrep : int = 100
    tol : float = 1e-8

Module-level constants cannot be assigned, and their names cannot be reused
for variables, arguments, attributes or functions (``dims`` constants are
macros in the generated C code).

Types
-----

========== ===============================================================
``int``    integer (``int`` in C: values must fit in 32 bits)
``float``  double-precision floating point
``dims``   integer constant usable as a matrix or vector size (module level only)
``dimv``   list of ``[rows, cols]`` pairs (module level only)
``pmat``   matrix of floats, ``pmat(rows, cols)``
``pvec``   vector of floats, ``pvec(size)``
``List``   fixed-size list, ``plist(<type>, <sizes>)``
class name an object of a user-defined class
========== ===============================================================

There is no ``bool`` type *(not supported yet)*.

Declarations
------------

Every variable is declared, with its type, before it is used:

.. code-block:: python

    k : int = 0
    x : float = 1.5
    A : pmat = pmat(n, m)       # sizes must be dims constants (or +, -, * of them)
    v : pvec = pvec(n)
    P : List = plist(int, n)    # element type int or float, size: dims
    obj : MyClass = MyClass()

- A variable cannot be declared twice, nor shadow a variable of an enclosing
  block.
- Variables are visible in the block (function, loop or ``if`` body) where
  they are declared, as in C: a variable declared inside an ``if`` cannot be
  used after it.
- Matrices, vectors, lists and objects must be declared outside loops and
  conditionals. Each declaration allocates memory, and prometeo computes the
  program's worst-case memory usage from the declarations: a declaration in a
  loop would allocate memory at every iteration and overflow the computed
  bound.
- Matrix and vector sizes must be ``dims`` constants: ``pmat(2, 2)`` is not
  accepted, declare ``k : dims = 2`` and use ``pmat(k, k)``.
- A scalar cannot be initialized with a matrix element (``x : float = A[0, 0]``)
  *(not supported yet)*: declare it, then assign it.
- Lists of matrices or vectors (``plist(pmat, sizes)``, with ``sizes`` a
  ``dimv`` constant) can only be declared as class attributes *(not supported
  yet as local variables)*.

Assignments
-----------

.. code-block:: python

    x = 2.0 * y - 1.0          # scalar expression
    x = A[i, j]                # read an element (as the whole right-hand side)
    x = f(y)                   # result of a call (as the whole right-hand side)
    A[i, j] = x                # write an element
    A[0:2, 1:3] = B            # copy a matrix into a block
    A[0:2, 1:3] = B[2:4, 0:2]  # copy a block into a block
    v[i] = x
    L[i] = A                   # make a List element refer to A (shared, as in Python)
    C = A * B                  # matrix product, sum (+) and difference (-)

- Matrix operators take two matrix variables (``A * B + C`` *(not supported
  yet)*), and the result must be stored in a different matrix than the
  operands: ``A = A * B`` is rejected because the transpiled code computes the
  result in place.
- ``B = A`` between two matrix (or vector) variables is rejected: in Python
  both names would refer to the same matrix, while in C ``B`` keeps its own
  memory, so later updates would differ. Use ``pmat_copy(A, B)``.
- Augmented assignments (``x += 1``) *(not supported yet)*.
- Elements of a List of ``int`` or ``float`` cannot be assigned or read
  *(not supported yet)*.

Expressions
-----------

Scalar expressions combine numbers, scalar variables, attributes and
constants with ``+``, ``-``, ``*``, ``/``, ``%`` and unary ``-``:

- int and float values cannot be mixed: write ``2.0 * x``, not ``2 * x``
  (an integer literal is accepted where a float is expected as a whole value,
  e.g. ``x : float = 0``).
- ``/`` requires float operands: on integers it gives a float in Python but
  truncates in C.
- ``%`` on integers gives a warning: for negative operands the result differs
  between Python and C. ``%`` is not defined on floats.
- ``//`` and ``**`` *(not supported yet)*.
- Matrix elements (``A[i, j]``) and calls cannot appear inside a larger
  expression *(not supported yet)*: assign them to a variable first.
- Indices are integer expressions, and must be in range: indices are not
  checked at run time in C.

Control flow
------------

.. code-block:: python

    for i in range(n):            # or range(start, stop); no step (not supported yet)
        ...
    while k < n:
        ...
    if x < 0.0:
        ...
    elif x < 1.0:
        ...
    else:
        ...

- Conditions are comparisons (``<``, ``<=``, ``>``, ``>=``, ``==``, ``!=``,
  also chained: ``0 < k < n``) of values of the same kind (int or float).
  ``and``, ``or``, ``not`` *(not supported yet)*.
- The loop variable can be used in indices (``A[i, n - 1 - i]``) and
  conditions, but not in other expressions or as a function argument *(not
  supported yet)*. It cannot be assigned, and is not visible after the loop.
- Reusing the loop variable of an enclosing loop gives a warning: after the
  inner loop, the outer variable has a different value in Python and in C.
- ``break``, ``continue``, ``pass`` and ``else`` clauses on loops *(not
  supported yet)*.

Functions
---------

.. code-block:: python

    def scale(A: pmat, alpha: float) -> None:
        ...
        return

    def trace(A: pmat) -> float:
        t : float = 0.0
        ...
        return t

- All arguments are annotated with ``int``, ``float``, ``pmat``, ``pvec``,
  ``List`` or a class name; matrices, vectors and lists are passed by
  reference. Default values, ``*args`` and ``**kwargs`` *(not supported yet)*;
  ``dims`` arguments *(not supported yet)*.
- The return type is ``int``, ``float``, ``pmat``, ``pvec`` or ``None``; a
  function that returns a value must end with a ``return`` statement.
- Defining two functions (or methods) with the same name and different
  argument types is accepted with a warning: the transpiled code supports
  overloading, but in Python only the last definition is used.

Classes
-------

.. code-block:: python

    class Model:
        def __init__(self) -> None:
            self.A : pmat = pmat(n, n)
            self.steps : List = plist(pmat, sizes)
            self.k : int = 0

        def step(self, x: float) -> float:
            ...

- Attributes are declared in ``__init__``, which takes no arguments other than
  ``self`` *(not supported yet)*.
- Methods take ``self`` as first argument (not annotated); there is no
  inheritance and there are no special methods other than ``__init__``.
- Elements of matrix attributes cannot be assigned directly
  (``self.A[i, j] = x``) *(not supported yet)*.

Printing
--------

.. code-block:: python

    print('text\n')
    print('k = %i\n' % k)       # one value per print; %d or %i for int, %f, %e, %g for float
    pmat_print(A)
    pvec_print(v)

The format must match the type of the value: in C, printing a float with
``%i`` prints garbage. f-strings and printing several values at once *(not
supported yet)*.

Built-in functions
------------------

========================================== ========================================
``pmat_print(A)``, ``pvec_print(v)``       print a matrix or vector
``pmat_fill(A, x)``                        set all elements of ``A`` to ``x``
``pmat_copy(A, B)``, ``pvec_copy(a, b)``   copy into ``B`` (``b``)
``pmat_tran(A, B)``                        ``B = A^T``
``pmat_hcat(A, B, C)``                     ``C = [A, B]``
``pmt_gemm(A, B, [C,] D)``                 ``D = beta C + alpha A B``, with the
                                           keyword arguments ``alpha=1.0`` and
                                           ``beta=0.0`` (float literals)
``pmt_gemm_nn(A, B, C, D)``                ``D = C + A B`` (also ``_nt``: ``A B^T``,
                                           ``_tn``: ``A^T B``)
``pmt_gead(alpha, A, B)``                  ``B = B + alpha A``
``pmt_potrf(A, L)``                        Cholesky factorization ``A = L L^T``
``pmt_potrsm(L, B)``                       solve ``L L^T X = B``, result in ``B``
``pmt_getrf(A, LU, ipiv)``                 LU factorization with pivoting
``pmt_trmm_rlnn(A, B, D)``                 ``D = B A``, ``A`` lower triangular
``pmt_syrk_ln(A, B, C, D)``                ``D = C + A B^T`` (lower triangle)
========================================== ========================================

The output of ``pmat_tran``, ``pmat_hcat``, ``pmt_gemm_*``, ``pmt_potrsm``,
``pmt_trmm_rlnn`` and ``pmt_syrk_ln`` must be a different matrix than the
other inputs: these cannot be computed in place. Accumulating
(``pmt_gemm_nn(A, B, C, C)``) and in-place factorizations
(``pmt_potrf(A, A)``) are fine.

Other functions of the Python implementation (e.g. ``pmat_vcat``,
``pmt_gemm_tt``, ``pmt_gemv_n``, ``pmt_potrsv``) cannot be transpiled *(not
supported yet)*.

Names
-----

Names cannot be C keywords (``double``, ``char``, ...), prometeo types or
built-in function names, and cannot start with ``c_pmt_``, ``blasfeo_`` or
``_Z``, which are used by the generated code.

Pure Python blocks
------------------

Lines between ``# pure >`` and ``# pure <`` are only run by the Python
interpreter, and are ignored by the checker and the transpiler. They can use
any Python code and library, e.g. to plot or check results with NumPy.

Memory
------

Transpiled programs allocate all matrices, vectors, lists and objects from a
heap whose size is computed by prometeo's static memory analysis. The
generated code checks every allocation against this bound and stops with
``prometeo: heap overflow`` instead of overwriting memory. By default the heap
is twice the computed bound; the factor can be set with the environment
variable ``PMT_HEAP_MARGIN`` (the tests use 1, so that any underestimated
bound is detected).

Known differences not detected by the checker
---------------------------------------------

- Integer overflow: Python integers are unbounded, C ``int`` values wrap around
  beyond 32 bits (undefined behavior in C).
- Out-of-range indices raise an ``IndexError`` in Python, but are not checked
  in C.
- Infinite recursion fails differently (``RecursionError`` in Python, stack
  overflow in C). Recursive functions must not declare matrices, vectors,
  lists or objects (the memory analysis rejects them).
