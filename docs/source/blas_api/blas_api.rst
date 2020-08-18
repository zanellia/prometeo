BLAS API
====================================

Below a description of prometeo's BLAS API can be found:

LEVEL 1 BLAS 
############

LEVEL 2 BLAS 
############

* General matrix-vector multiplication (GEMV) 

.. math::


    z \leftarrow \beta \cdot y + \alpha \cdot  \text{op}(A)  x

.. code-block:: python

    pmt_gemv(A[.T], x, [y], z, [alpha=1.0], [beta=1.0])

LEVEL 3 BLAS 
############

* General matrix-matrix multiplication (GEMM) 

.. math::

    D \leftarrow \beta \cdot C + \alpha \cdot \text{op}(A) \text{op}(B)

.. code-block:: python

    pmt_gemm(A[.T], B[.T], [C], D, [alpha=1.0], [beta=1.0])
