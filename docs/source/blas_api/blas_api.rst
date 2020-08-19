BLAS/LAPACK API
====================================

Below a description of prometeo's BLAS/LAPACK API can be found:

LEVEL 1 BLAS 
############

LEVEL 2 BLAS 
############

* General matrix-vector multiplication (GEMV) 

.. math::


    z \leftarrow \beta \cdot y + \alpha \cdot  \text{op}(A)  x

.. code-block:: python

    pmt_gemv(A[.T], x, [y], z, [alpha=1.0], [beta=0.0])

* Solve linear system with (lower or upper) triangular matrix coefficient (TRSV) 

.. math::


    \text{op}(A)\,x = b


.. code-block:: python

    pmt_trsv(A[.T], b, [lower=True])

* Matrix-vector multiplication with (lower or upper) triangular matrix coefficient (TRMV) 

.. math::


    z \leftarrow \text{op}(A)\,x


.. code-block:: python

    pmt_trmv(A[.T], x, z, [lower=True])

LEVEL 3 BLAS 
############

* General matrix-matrix multiplication (GEMM) 

.. math::

    D \leftarrow \beta \cdot C + \alpha \cdot \text{op}(A) \, \text{op}(B)

.. code-block:: python

    pmt_gemm(A[.T], B[.T], [C], D, [alpha=1.0], [beta=0.0])

* Symmetric rank :math:`k` update (SYRK) 

.. math::

    D \leftarrow \beta \cdot C + \alpha \cdot \text{op}(A) \,\text{op}(B)
    
with :math:`C` and :math:`D` lower triangular.

.. code-block:: python

    pmt_syrk(A[.T], B[.T], [C], D, [alpha=1.0], [beta=0.0])

* Triangular matrix-matrix multiplication (TRMM) 

.. math::

    D \leftarrow \alpha \cdot B\, A^{\top}

with :math:`B` upper triangular or 


.. math::

    D \leftarrow \alpha \cdot A\, B

with :math:`A` lower triangular. 

.. code-block:: python

    pmt_trmm(A[.T], B, D, [alpha=1.0], [beta=0.0])
