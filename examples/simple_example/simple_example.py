from prometeo import *

nv : dims = 10

def foo(a: int) -> int:
    return a + 1

def main() -> int:

    A: pmat = pmat(nv, nv)
    for i in range(nv):
        for j in range(nv):
            A[i, j] = 1.0

    B: pmat = pmat(nv, nv)
    for i in range(nv):
        B[0, i] = 2.0

    D: pmat = pmat(nv, nv)

    a : int = 1
    b : int = 1
    c : int = 1
    a = (a + b)*c
    b = foo(b)
    
    pmat_print(A)
    pmat_print(B)
    pmt_gemm(A,B,D)
    pmat_print(D)

    return 0

