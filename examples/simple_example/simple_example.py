from prometeo import *

def main() -> None:

    n: int = 10
    A: pmat = pmat(n, n)
    for i in range(10):
        for j in range(10):
            A[i, j] = 1.0

    B: pmat = pmat(n, n)
    for i in range(10):
        B[0, i] = 2.0

    C: pmat = pmat(n, n)

    C = A * B
    pmat_print(C)

