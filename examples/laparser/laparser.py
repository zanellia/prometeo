from prometeo import *

nx: dims  = 2

def main() -> int:

    A: pmat = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.3
    A[1,1] = 0.8

    B: pmat = pmat(nx, nx)
    B[0,0] = 1.0  
    B[0,1] = 2.0
    B[1,0] = 0.0
    B[1,1] = 1.0

    D: pmat = pmat(nx, nx)
    D[0,0] = 1.0  
    D[0,1] = 3.0
    D[1,0] = 2.0
    D[1,1] = 1.0

    C: pmat = pmat(nx, nx)

    pparse('C = A - A.T \ (B * D).T')

    pmat_print(C)
