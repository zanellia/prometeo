from prometeo import *

nm:  dims = 10
nx:  dims = 2*nm
nu:  dims = nm
nxu: dims = nx + nu
N:   dims = 5

def main() -> int:
    # number of repetitions for timing
    nrep : int = 10000

    # set up dynamics TODO(needs discretization!)
    A: pmat = pmat(nx, nx)
    Ac11 : pmat = pmat(nm,nm)
    for i in range(nm):
        Ac11[i,i] = 1.0

    Ac12 : pmat = pmat(nm,nm)
    for i in range(nm):
        Ac12[i,i] = 1.0

    Ac21 : pmat = pmat(nm,nm)
    for i in range(nm):
        Ac21[i,i] = -2.0

    for i in range(nm-1):
        Ac21[i+1,i] = 1.0
        Ac21[i,i+1] = 1.0

    Ac22 : pmat = pmat(nm,nm)
    for i in range(nm):
        Ac22[i,i] = 1.0

    for i in range(nm):
        for j in range(nm):
            A[i,j] = Ac11[i,j]

    for i in range(nm):
        for j in range(nm):
            A[i,nm+j] = Ac12[i,j]

    for i in range(nm):
        for j in range(nm):
            A[nm+i,j] = Ac21[i,j]

    for i in range(nm):
        for j in range(nm):
            A[nm+i,nm+j] = Ac22[i,j]


    tmp : float = 0.0
    for i in range(nx):
        tmp = A[i,i]
        tmp = tmp + 1.0
        A[i,i] = tmp

    B: pmat = pmat(nx, nu)

    for i in range(nu):
        B[nm+i,i] = 1.0

    Q: pmat = pmat(nx, nx)
    for i in range(nx):
        Q[i,i] = 1.0

    R: pmat = pmat(nu, nu)
    for i in range(nu):
        R[i,i] = 1.0

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
