from prometeo import *

r : dims = 4

def main() -> int:

    A: pmat = pmat(r, r)
    for i in range(r):
        for j in range(r):
            A[i, j] = 1.0

    B: pmat = pmat(r, r)
    for i in range(r):
        B[0, i] = 2.0

    C: pmat = pmat(r, r)
    D: pmat = pmat(r, r)

    pmat_print(A)
    pmat_print(B)
    pmt_gemm(A.T, B, C, alpha=1.0, beta=0.1)
    # pmt_gemm(A, B, C, D)
    pmt_gemm(A, B, C)
    # pmt_gemm(A.T, B, C)
    # pmt_gemm(A, B, C)
    # pmt_gemm(A, B, C)

    return 0

