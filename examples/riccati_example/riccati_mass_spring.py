from prometeo import *

nm: dims = 4
nx: dims  = 2*nm
# nx: dims  = 2
# sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
# sizes: dimv = [[8,8], [8,8], [8,8], [8,8], [8,8]]
nu: dims  = nm
nxu: dims = nx + nu
N:  dims  = 5

class qp_data:
    A: pmat = pmat(nx, nx) 
    B: pmat = pmat(nx, nu) 
    Q: pmat = pmat(nx, nx) 
    R: pmat = pmat(nu, nu) 

    def factorize(self) -> None:
        M: pmat = pmat(nxu, nxu)
        Lxx: pmat = pmat(nx, nx)
        Q: pmat = pmat(nx, nx)
        R: pmat = pmat(nu, nu)
        RSQ: pmat = pmat(nxu, nxu)
        BA: pmat = pmat(nx, nxu)
        BAt: pmat = pmat(nxu, nx)
        w_nxu_nx: pmat = pmat(nxu, nx)

        pmat_hcat(self.B, self.A, BA)
        pmat_tran(BA, BAt)
        pmat_copy(self.Q, Q)
        pmat_copy(self.R, R)
        RSQ[0:nu,0:nu] = R
        RSQ[nu:nu+nx,nu:nu+nx] = Q
        pmt_potrf(self.Q, Lxx)
        M[nu:nu+nx,nu:nu+nx] = Lxx
        for i in range(1, N):
            pmt_trmm_rlnn(M, BAt, w_nxu_nx)

            pmt_syrk_ln(w_nxu_nx, w_nxu_nx, RSQ, M)
            pmt_potrf(M, M)
            # pmat_print(M)

        return

def main() -> int:

    A: pmat = pmat(nx, nx)
    Ac11 : pmat = pmat(nm,nm)
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

    qp : qp_data = qp_data() 

    pmat_copy(A, qp.A)
    pmat_copy(B, qp.B)
    pmat_copy(Q, qp.Q)
    pmat_copy(R, qp.R)

    qp.factorize()
    
    return 0
