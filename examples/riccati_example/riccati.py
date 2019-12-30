# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims = 2
nu: dims = 2
N:  dims = 5
# sizes: dim = N*[nx, nx]

class qp_data:
    C: pmat[nu,nu] = pmat(nx,nu)
    A: List[pmat, sizes]  = prmt_list(pmat, sizes)
    B: List[pmat, sizes]  = prmt_list(pmat, sizes)
    Q: List[pmat, sizes]  = prmt_list(pmat, sizes)
    R: List[pmat, sizes]  = prmt_list(pmat, sizes)
    P: List[pmat, sizes]  = prmt_list(pmat, sizes)

    fact: List[pmat, sizes] = prmt_list(pmat, sizes)

    def factorize(self) -> None:
        for i in range(N):
            pmt_potrf(self.Q[i], self.fact[i])

        return

def main() -> None:

    A: pmat[nu,nu] = pmat(nx, nx)
    B: pmat[nu,nu] = pmat(nx, nu)
    Q: pmat[nu,nu] = pmat(nx, nx)
    R: pmat[nu,nu] = pmat(nu, nu)
    P: pmat[nu,nu] = pmat(nx, nx)

    fact: pmat[nu,nu] = pmat(nx, nx)

    qp : qp_data = qp_data() 

    for i in range(N):
        qp.A[i] = A

    for i in range(N):
        qp.B[i] = B

    for i in range(N):
        qp.Q[i] = Q

    for i in range(N):
        qp.R[i] = R

    for i in range(N):
        qp.fact[i] = fact

    qp.factorize()

    # A_ : pmat[2,2] = qp.A[0]
    # A_ : pmat[2,2] = pmat(2,2)
    # A_ = qp.A[0]
    # n_list: List[int] = prmt_list(int, 10) 
    # n_list[0] = 1

    # test_class: p_class = p_class()
    # test_class.attr_1 = 2

    # j: int = 0
    # for i in range(10):
    #     j = j + 1

    # while j > 0:
    #     j = j - 1

    # n: int = 10
    # A: pmat[2,2] = pmat(n, n)
    # A[0,2] = -2.0

    # for i in range(2):
    #     A[0,i] = A[0,i]

    # pmat_fill(A, 1.0)

    # B: pmat[n,n] = pmat(n, n)
    # for i in range(2):
    #     B[0,i] = A[0,i]
    # pmat_fill(B, 2.0)

    # C: pmat[n,n] = pmat(n, n)

    # test_class.method_2(A, B, C)

    # pmat_list: List[pmat] = prmt_list(pmat, 10)
    # pmat_list[0] = A

    # C = A * B
    # pmat_print(C)
    # C = A + B
    # pmat_print(C)
    # C = A - B
    # pmat_print(C)

    # function1(A, B, C)
    # function1(pmat_list[0], B, C)

    # pmat_fill(A, 0.0)
    # for i in range(10):
    #     A[i,i] = 1.0

    # pmat_print(A)

    # a : pvec[10] = pvec(10)
    # a[1] = 3.0
    # b : pvec = pvec(3)
    # b[0] = a[1]
    # b[1] = A[0, 2]
    # A[0,2] = a[0]

    # el : float
    # el = a[1]
    # el = A[1, 1]
    # pvec_print(a)
    # pvec_print(b)

    # c : pvec = pvec(10)
    # c = A * a
    # pvec_print(c)

    # # test LU solve
    # ipiv: List[int] = prmt_list(int, 2) 
    # fact : pmat[2,2] = pmat(2, 2)
    # M : pmat[2,2] = pmat(2,2)
    # pmt_getrf(M, fact, ipiv)
    # res: pvec[2] = pvec(2)
    # rhs: pvec[2] = pvec(2)
    # rhs[0] = 1.0
    # rhs[1] = -3.0
    # pmt_getrs(rhs, fact, ipiv, res)

    # # test Cholesky solve
    # M[0,0] = 1.0
    # M[0,1] = 0.1
    # M[1,0] = 0.1
    # M[1,1] = 1.0
    # pmt_potrf(M, fact)
    # pmt_potrs(rhs, fact, res)
