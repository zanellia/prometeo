from prometeo import *

nx:  dims = 2
nu:  dims = 2
nxu: dims = nx + nu
N:   dims = 5

def main() -> int:

    # number of repetitions for timing
    nrep : int = 10000

    A: pmat = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.3
    A[1,1] = 0.8

    B: pmat = pmat(nx, nu)
    B[0,0] = 1.0  
    B[1,1] = 1.0

    Q: pmat = pmat(nx, nx)
    Q[0,0] = 1.0  
    Q[1,1] = 1.0

    R: pmat = pmat(nu, nu)
    R[0,0] = 1.0  
    R[1,1] = 1.0

    RSQ: pmat = pmat(nxu, nxu)
    Lxx: pmat = pmat(nx, nx)
    M: pmat = pmat(nxu, nxu)
    w_nxu_nx: pmat = pmat(nxu, nx)
    BAt : pmat = pmat(nxu, nx)
    BA : pmat = pmat(nx, nxu)
    pmat_hcat(B, A, BA)
    pmat_tran(BA, BAt)

    RSQ[0:nu,0:nu] = R
    RSQ[nu:nu+nx,nu:nu+nx] = Q

    # array-type Riccati factorization
    for i in range(nrep):
        pmt_potrf(Q, Lxx)
        M[nu:nu+nx,nu:nu+nx] = Lxx
        for i in range(1, N):
            pmt_trmm_rlnn(Lxx, BAt, w_nxu_nx)
            pmt_syrk_ln(w_nxu_nx, w_nxu_nx, RSQ, M)
            pmt_potrf(M, M)
            Lxx[0:nx,0:nx] = M[nu:nu+nx,nu:nu+nx]

    return 0

