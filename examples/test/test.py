# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims = 2
nu: dims = 2
N:  dims = 5

class qp_data:
    C: pmat  = pmat(nx,nu)
    A: List  = plist(pmat, sizes)
    l: List  = plist(int, 5)
    B: List  = plist(pmat, sizes)
    Q: List  = plist(pmat, sizes)
    R: List  = plist(pmat, sizes)
    P: List  = plist(pmat, sizes)

    fact: List = plist(pmat, sizes)

    def factorize(self) -> None:
        res: pmat = pmat(nx, nx)
        Bt: pmat = pmat(nx, nx)
        for i in range(N):
            pmt_gemm_nn(self.P[i], self.B[i], res, res)
            pmat_tran(self.B[i], Bt)
            pmt_gemm_nn(Bt, res, self.R[i], res)
            pmt_potrf(res, self.fact[i])
            # pmt_potrsm(res, self.fact[i])

        return

def main() -> None:

    # test assignments
    n: int = 10
    M: pmat = pmat(n, n)

    a : pvec = pvec(10)
    a[1] = 3.0

    d : float = 10.0

    # float to pmat
    M[0,1] = d

    # float (const) to pmat 
    M[0,1] = 1.0

    # pmat to float
    d = M[0, 1]

    # float to pvec
    a[0] = d

    # float (const) to pvec 
    a[0] = 1.0

    # pvec to float
    d = a[0]

    # subscripted pmat to pmat 
    for i in range(2):
        M[0,i] = M[0,i]

    # subscripted pvec to pvec
    a[0] = a[1]

    # subscripted pmat to pvec
    a[1] = M[0, 2]

    # subscripted pvec to pmat
    M[0, 2] = a[1]

    # run Riccati code
    A: pmat = pmat(nx, nx)
    B: pmat = pmat(nx, nu)
    Q: pmat = pmat(nx, nx)
    R: pmat = pmat(nu, nu)
    P: pmat = pmat(nx, nx)

    mat_list: List  = plist(pmat, sizes)

    fact: pmat = pmat(nx, nx)

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
