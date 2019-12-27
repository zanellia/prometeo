# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo import *

def main() -> None:

    # test assignments
    n: int = 10
    A: pmat[2,2] = pmat(n, n)

    a : pvec[10] = pvec(10)
    a[1] = 3.0

    d : float = 10.0

    # float to pmat
    A[0,1] = d

    # float (const) to pmat 
    A[0,1] = 1.0

    # pmat to float
    d = A[0, 1]

    # float to pvec
    a[0] = d

    # float (const) to pvec 
    a[0] = 1.0

    # pvec to float
    d = a[0]

    # subscripted pmat to pmat 
    for i in range(2):
        A[0,i] = A[0,i]

    # subscripted pvec to pvec
    a[0] = a[1]

    # subscripted pmat to pvec
    a[1] = A[0, 2]

    # subscripted pvec to pmat
    A[0, 2] = a[1]

# # UNCOMMENT THESE LINES TO EXECUTE 
# # if __name__ == "__main__":
    # # execute only if run as a script
    # # main()
