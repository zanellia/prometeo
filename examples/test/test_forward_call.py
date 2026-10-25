from prometeo import *

n : dims = 3

# functions can be called before they are defined

def fill(A: pmat, value: float) -> None:
    for i in range(n):
        for j in range(n):
            A[i, j] = value
    add_to_diagonal(A, twice(value))
    return

def add_to_diagonal(A: pmat, value: float) -> None:
    tmp : float = 0.0
    for i in range(n):
        tmp = A[i, i]
        tmp = tmp + value
        A[i, i] = tmp
    return

def twice(value: float) -> float:
    return 2.0 * value

def main() -> int:
    A: pmat = pmat(n, n)
    fill(A, 0.5)
    pmat_print(A)
    return 0
