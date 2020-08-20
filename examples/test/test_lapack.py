from prometeo import *

n : dims = 5


def main() -> int:

    C : pmat = pmat(n,n)
    for i in range(5):
        C[i,i] = 2.0

    D : pmat = pmat(n,n)

    ipiv : List = plist(int, n)

    pmt_getrf(C, D, ipiv)
    pmat_print(D)

    pmt_potrf(C, D)
    pmat_print(D)

    return 0
