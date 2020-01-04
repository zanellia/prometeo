from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2]]
class p_class:
    attr_1: int = 1
    attr_2: float = 3.0
    attr_3: pmat = pmat(10, 10) 

    def method_2(self, A: pmat[2,2], B: pmat[2,2], C: pmat[2,2]) -> None:
        C = A * B
        pmat_print(C)
        return

def function1(A: pmat[2,2], B: pmat[2,2], C: pmat[2,2]) -> None:
    C = A * B
    pmat_print(C)
    attr_3: pmat = pmat(10, 10)
    return

def main() -> None:

    n_list: List = plist(int, 10) 
    n_list[0] = 1

    test_class: p_class = p_class()
    test_class.attr_1 = 2

    j: int = 0
    for i in range(10):
        j = j + 1

    while j > 0:
        j = j - 1

    n: int = 10
    A: pmat = pmat(n, n)
    A[0,2] = -2.0

    for i in range(2):
        A[0,i] = A[0,i]

    pmat_fill(A, 1.0)

    B: pmat = pmat(n, n)
    for i in range(2):
        B[0,i] = A[0,i]
    pmat_fill(B, 2.0)

    C: pmat = pmat(n, n)

    test_class.method_2(A, B, C)

    pmat_list: List = plist(pmat, sizes)
    pmat_list[0] = A

    C = A * B
    pmat_print(C)
    C = A + B
    pmat_print(C)
    C = A - B
    pmat_print(C)

    function1(A, B, C)
    function1(pmat_list[0], B, C)

    pmat_fill(A, 0.0)
    for i in range(10):
        A[i,i] = 1.0

    pmat_print(A)

    a : pvec = pvec(10)
    a[1] = 3.0
    b : pvec = pvec(3)
    b[0] = a[1]
    b[1] = A[0, 2]
    A[0,2] = a[0]

    el : float = 1.0
    el = a[1]
    el = A[1, 1]
    pvec_print(a)
    pvec_print(b)

    c : pvec = pvec(10)
    c = A * a
    pvec_print(c)

    # test LU solve
    ipiv: List = plist(int, 2) 
    fact : pmat = pmat(2, 2)
    M : pmat = pmat(2,2)
    pmt_getrf(M, fact, ipiv)
    res: pvec = pvec(2)
    rhs: pvec = pvec(2)
    rhs[0] = 1.0
    rhs[1] = -3.0
    pmt_getrsv(fact, ipiv, rhs)

    # test Cholesky solve
    M[0,0] = 1.0
    M[0,1] = 0.1
    M[1,0] = 0.1
    M[1,1] = 1.0
    pmt_potrf(M, fact)
    pmt_potrsv(fact, rhs)

# UNCOMMENT THESE LINES TO EXECUTE 
# if __name__ == "__main__":
    # execute only if run as a script
    # main()
