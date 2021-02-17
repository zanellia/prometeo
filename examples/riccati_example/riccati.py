from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims  = 2
nxu: dims = 4
nu: dims  = 2
N:  dims  = 5

class qp_data:
    def __init__(self) -> None:
        self.A: List = plist(pmat, sizes)
        self.B: List = plist(pmat, sizes)
        self.Q: List = plist(pmat, sizes)
        self.R: List = plist(pmat, sizes)
        self.P: List = plist(pmat, sizes)

    def factorize(self) -> None:
        M: pmat = pmat(nxu, nxu)
        Mxx: pmat = pmat(nx, nx)
        L: pmat = pmat(nxu, nxu)
        Q: pmat = pmat(nx, nx)
        R: pmat = pmat(nu, nu)
        BA: pmat = pmat(nx, nxu)
        BAtP: pmat = pmat(nxu, nx)
        pmat_copy(self.Q[N-1], self.P[N-1])

        for i in range(1, N):
            pmat_hcat(self.B[N-i], self.A[N-i], BA)
            pmat_fill(BAtP, 0.0)
            pmt_gemm_tn(BA, self.P[N-i], BAtP, BAtP)

            pmat_copy(self.Q[N-i], Q)
            pmat_copy(self.R[N-i], R)
            pmat_fill(M, 0.0)
            M[0:nu,0:nu] = R[0:nu,0:nu]
            M[nu:nu+nx,nu:nu+nx] = Q

            pmt_gemm_nn(BAtP, BA, M, M)
            pmat_fill(L, 0.0)
            pmt_potrf(M, L)
            pmat_print(L)

            Mxx[0:nx, 0:nx] = L[nu:nu+nx, nu:nu+nx]

            pmat_fill(self.P[N-i-1], 0.0)
            pmt_gemm_nt(Mxx, Mxx, self.P[N-i-1], self.P[N-i-1])
            # pmat_print(self.P[N-i-1])

        return

def main() -> int:

    A: pmat = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.3
    A[1,1] = 0.8

    B: pmat = pmat(nx, nu)
    B[0,0] = 1.0  
    B[0,1] = 0.0
    B[1,0] = 0.0
    B[1,1] = 1.0

    Q: pmat = pmat(nx, nx)
    Q[0,0] = 1.0  
    Q[0,1] = 0.0
    Q[1,0] = 0.0
    Q[1,1] = 1.0

    R: pmat = pmat(nu, nu)
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
    
    return 0
