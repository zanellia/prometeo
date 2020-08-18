from prometeo import *

r : dims = 4

def main() -> int:

    # LEVEL 3
    A: pmat = pmat(r, r)
    for i in range(r):
        for j in range(r):
            A[i, j] = 1.0

    B: pmat = pmat(r, r)
    for i in range(r):
        B[0, i] = 2.0

    C: pmat = pmat(r, r)

    print("A:\n")
    pmat_print(A)
    print("B:\n")
    pmat_print(B)

    print("gemm(A, B, C):\n")
    pmt_gemm(A, B, C)
    pmat_print(C)

    for i in range(r):
        for j in range(r):
            C[i, j] = 5.0

    print("gemm(A, B, C, beta=1.0):\n")
    pmt_gemm(A, B, C, beta=1.0)
    pmat_print(C)

    D: pmat = pmat(r, r)
    pmt_gemm(A, B, C, D)
    print("gemm(A, B, C, D):\n")
    pmat_print(C)

    pmt_gemm(A, B.T, C, alpha=0.5, beta=0.5)
    print("gemm(A, B.T, C, alpha=0.0, beta=0.1):\n")
    pmat_print(C)

    # LEVEL 2
    x: pvec = pvec(r)
    z: pvec = pvec(r)

    for i in range(r):
            x[i] = 1.0

    y: pvec = pvec(r)
    for i in range(r):
        y[i] = 2.0

    pmt_gemv(A, x, z)
    print("gemv(A, x, z):\n")
    pvec_print(z)

    pmt_gemv(A.T, x, z)
    print("gemv(A.T, x, z):\n")
    pvec_print(z)

    pmt_gemv(A.T, x, y, z, beta=0.1)
    print("gemv(A.T, x, y, z, beta=0.1):\n")
    pvec_print(z)

    return 0

