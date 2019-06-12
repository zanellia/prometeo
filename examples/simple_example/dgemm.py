# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo.linalg import *
from prometeo.auxl import *

def main() -> None:

    n: int = 10
    A: pmat = pmat(n, n)

    B: pmat = pmat(n, n)
    for i in range(2):
        B[0][i] = A[0][i]

    C: pmat = pmat(n, n)

    C = A * B
    pmat_print(C)

if __name__ == "__main__":
    main()
