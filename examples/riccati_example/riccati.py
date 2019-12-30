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
        Mxut: pmat[nu, nxu] = pmat(nu, nxu)
        Mxx: pmat[nx, nx] = pmat(nx, nx)
        Mxu: pmat[nxu, nu] = pmat(nxu, nu)
        Lu: pmat[nu, nu] = pmat(nu, nu)
        Lxu: pmat[nxu, nxu] = pmat(nxu, nxu)
        Q: pmat[nx, nx] = pmat(nx, nx)
        R: pmat[nu, nu] = pmat(nu, nu)
        Bt: pmat[nx, nx] = pmat(nx, nx)
        At: pmat[nx, nx] = pmat(nx, nx)
        BAt: pmat[nxu, nx] = pmat(nxu, nx)
        BA: pmat[nx, nxu] = pmat(nx, nxu)
        BAtP: pmat[nxu, nx] = pmat(nxu, nx)
        pmat_copy(self.Q[N-1], self.P[N-1])
        for i in range(1, N):
            pmat_tran(self.B[N-i], Bt)
            pmat_tran(self.A[N-i], At)
            pmat_vcat(Bt, At, BAt)
            pmt_gemm(BAt, self.P[N-i], BAtP, BAtP)

            pmat_copy(self.Q[N-i], Q)
            pmat_copy(self.R[N-i], R)
            for j in range(nu):
                for k in range(nu):
                    M[j,k] = R[j,k]
            for j in range(nx):
                for k in range(nx):
                    M[nu+j,nu+k] = Q[j,k]

            pmat_tran(BAt, BA)

            pmt_gemm(BAtP, BA, M, M)
            for j in range(nu):
                for k in range(nu):
                    Mu[j,k] = M[j,k]
            pmt_potrf(Mu, Lu)

            for j in range(nx):
                for k in range(nx):
                    Mxut[k,nu+j] = M[j,k]

            for j in range(nx):
                for k in range(nx):
                    Mxx[k,j] = M[nu+j,nu+k]

            pmt_potrsm(Lu, Mxut)
            pmat_tran(Mxut, Mxu)
            pmt_gemm(Mxut, Mxu, self.P[N-i-1], self.P[N-i-1])
            pmt_gead(-1.0, self.P[N-i-1], Mxx)
            pmat_copy(Mxx, self.P[N-i-1])
            pmat_print(self.P[N-i-1])

        return

def main() -> None:

    A: pmat[nu,nu] = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.0
    A[1,1] = 0.8

    B: pmat[nx,nu] = pmat(nx, nu)
    B[0,0] = 1.0  
    B[0,1] = 0.0
    B[1,0] = 0.0
    B[1,1] = 1.0

    Q: pmat[nx,nx] = pmat(nx, nx)
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
