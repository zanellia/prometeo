Linear algebra
==============

Matrix expressions
##################

The recommended way to do linear algebra in prometeo is with NumPy's syntax:

.. code-block:: python

    P = Q + A.T @ P_next @ A - K.T @ R @ K
    L = cholesky(R + B.T @ P @ B)
    K = -cho_solve(L, B.T @ P @ A)
    K[0:n, n:] = B.T                     # blocks
    y = A @ x + B @ u                    # vectors
    c : float = x @ Q @ x                # dot products
    W = U * V                            # elementwise products

Each assignment is translated into calls of the BLASFEO-based routines below,
with temporaries allocated statically; sizes are checked at compile time when
they are known. See :doc:`the language reference <../language/language>`
(section *Matrix expressions*) for the operations, the rules, and how
expressions are translated.

Routines
########

The routines can also be called directly, e.g. to control exactly which
operations are performed. Matrices are ``pmat``, vectors ``pvec``; outputs
are the last arguments, written in place. Sizes are checked (an error is
raised in Python, the C program stops with a message).

Copies and printing
*******************

.. code-block:: python

    pmat_fill(A, value)        # A[i, j] = value
    pmat_copy(A, B)            # B = A
    pmat_tran(A, B)            # B = A.T (B must be a different matrix)
    pmat_hcat(A, B, C)         # C = [A, B]
    pvec_copy(a, b)            # b = a
    pmat_print(A)
    pvec_print(v)

BLAS
****

* General matrix-matrix multiplication (GEMM)

.. math::

    D \leftarrow \beta \cdot C + \alpha \cdot A \, B

.. code-block:: python

    pmt_gemm(A, B, C, D, alpha=1.0, beta=0.0)
    pmt_gemm(A, B, D)                    # D = A B (alpha and beta also accepted)

and, with :math:`D \leftarrow C + \text{op}(A) \, \text{op}(B)`:

.. code-block:: python

    pmt_gemm_nn(A, B, C, D)              # D = C + A B
    pmt_gemm_nt(A, B, C, D)              # D = C + A B^T
    pmt_gemm_tn(A, B, C, D)              # D = C + A^T B

``C`` and ``D`` can be the same matrix, ``A`` and ``B`` must be different
from ``D``.

* Matrix addition

.. math::

    B \leftarrow B + \alpha \cdot A

.. code-block:: python

    pmt_gead(alpha, A, B)

* Symmetric rank :math:`k` update (SYRK)

.. math::

    D \leftarrow C + A \, B^{\top}

computing only the lower triangle of :math:`D`.

.. code-block:: python

    pmt_syrk_ln(A, B, C, D)

* Triangular matrix-matrix multiplication (TRMM)

.. math::

    D \leftarrow B \, A

with :math:`A` lower triangular.

.. code-block:: python

    pmt_trmm_rlnn(A, B, D)

LAPACK
******

* Cholesky factorization (POTRF)

.. math::

    A = L \, L^{\top}

with :math:`L` lower triangular and :math:`A` symmetric positive definite.

.. code-block:: python

    pmt_potrf(A, L)

* Solution of :math:`L \, L^{\top} X = B` with the Cholesky factor (POTRS)

.. math::

    B \leftarrow (L \, L^{\top})^{-1} B

.. code-block:: python

    pmt_potrsm(L, B)

The upper triangle of ``L`` is overwritten with the transpose of the lower
one (``cho_solve`` in matrix expressions works on a copy).

* LU factorization with row pivoting (GETRF)

.. math::

    P \, A = L \, U

.. code-block:: python

    ipiv : List = plist(int, n)
    pmt_getrf(A, LU, ipiv)

``LU`` contains :math:`L` (unit lower triangular) and :math:`U`, ``ipiv``
the row permutation.
