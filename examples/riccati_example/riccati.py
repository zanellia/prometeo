# UNCOMMENT THESE LINES TO EXECUTE 
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims  = 2
nxu: dims = 4
nu: dims  = 2
N:  dims  = 5

class qp_data:
    A: List[pmat, sizes] = plist(pmat, sizes)
    B: List[pmat, sizes] = plist(pmat, sizes)
    Q: List[pmat, sizes] = plist(pmat, sizes)
    R: List[pmat, sizes] = plist(pmat, sizes)
    P: List[pmat, sizes] = plist(pmat, sizes)

    fact: List[pmat, sizes] = plist(pmat, sizes)

    def factorize(self) -> None:
        M: pmat[nxu, nxu] = pmat(nxu, nxu)
        Mu: pmat[nu, nu] = pmat(nu, nu)
        Lu: pmat[nu, nu] = pmat(nu, nu)
        Q: pmat[nx, nx] = pmat(nx, nx)
        R: pmat[nu, nu] = pmat(nu, nu)
        Bt: pmat[nx, nx] = pmat(nx, nx)
        At: pmat[nx, nx] = pmat(nx, nx)
        BAt: pmat[nxu, nx] = pmat(nxu, nx)
        BA: pmat[nx, nxu] = pmat(nx, nxu)
        BAtP: pmat[nxu, nx] = pmat(nxu, nx)
        pmat_copy(self.P[N-1], self.Q[N-1])
        for i in range(N-1, 0):
            pmat_tran(self.B[i], Bt)
            pmat_tran(self.A[i], At)
            pmat_vcat(Bt, At, BAt)
            pmt_gemm(BAt, self.P[i], BAtP, BAtP)
            pmat_copy(self.Q[i], Q)
            pmat_copy(self.R[i], R)
            for j in range(nu):
                for k in range(nu):
                    M[i,j] = R[i,j]
            for j in range(nx):
                for k in range(nx):
                    M[nu+i,nu+j] = Q[nx,nx]

            pmat_tran(BAt, BA)
            pmt_gemm(BAtP, BA, M, M)
            for j in range(nu):
                for k in range(nu):
                    Mu[j,j] = M[j,j]
            pmt_potrf(Mu, Lu)
            # pmt_gemm(Bt, res, self.R[i], res)
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
