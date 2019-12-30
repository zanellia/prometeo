# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims = 2
nu: dims = 2
N:  dims = 5

class qp_data:
    A: List[pmat, sizes]  = plist(pmat, sizes)
    B: List[pmat, sizes]  = plist(pmat, sizes)
    Q: List[pmat, sizes]  = plist(pmat, sizes)
    R: List[pmat, sizes]  = plist(pmat, sizes)
    P: List[pmat, sizes]  = plist(pmat, sizes)

    fact: List[pmat, sizes] = plist(pmat, sizes)

    def factorize(self) -> None:
        res: pmat[nx, nx] = pmat(nx, nx)
        Bt: pmat[nx, nx] = pmat(nx, nx)
        for i in range(N):
            pmt_gemm(self.P[i], self.B[i], res, res)
            pmat_tran(self.B[i], Bt)
            pmt_gemm(Bt, res, self.R[i], res)
            pmt_potrf(res, self.fact[i])
            # pmt_potrsm(res, self.fact[i])

        return

def main() -> None:

    A: pmat[nu,nu] = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.0
    A[1,1] = 0.8

    B: pmat[nu,nu] = pmat(nx, nu)
    B[0,0] = 1.0  
    B[0,1] = 0.0
    B[1,0] = 0.0
    B[1,1] = 1.0

    Q: pmat[nu,nu] = pmat(nx, nx)
    Q[0,0] = 1.0  
    Q[0,1] = 0.0
    Q[1,0] = 0.0
    Q[1,1] = 1.0

    R: pmat[nu,nu] = pmat(nu, nu)
    R[0,0] = 1.0  
    R[0,1] = 0.0
    R[1,0] = 0.0
    R[1,1] = 1.0

    qp : qp_data = qp_data() 

    for i in range(N):
        qp.A[i] = A

    for i in range(N):
        qp.B[i] = B

    for i in range(N):
        qp.Q[i] = Q

    for i in range(N):
        qp.R[i] = R

    qp.factorize()
