from prometeo import *
# pure >
import numpy as np
# pure <

n : dims = 10

def main() -> int:

    A: pmat = pmat(n, n)
    for i in range(n):
        for j in range(n):
            A[i, j] = 1.0

    # pure >
    M = np.array([[1.0, 2.0],[0.0, 0.5]])
    print('\neigenvalues of M computed with '
        'numpy in pure Python block:\n\n',
        np.linalg.eigvals(M), '\n')
    # pure <

    B: pmat = pmat(n, n)
    for i in range(n):
        B[0, i] = 2.0

    C: pmat = pmat(n, n)

    pmat_print(A)
    pmat_print(B)
    C = A * B
    pmat_print(C)
    return 0
