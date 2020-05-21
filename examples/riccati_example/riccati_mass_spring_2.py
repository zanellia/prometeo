from prometeo import *

nm: dims = 4
nx: dims  = 2*nm
sizes: dimv = [[8,8], [8,8], [8,8], [8,8], [8,8]]
nu: dims  = nm
nxu: dims = nx + nu
N:  dims  = 5

class qp_data:
    A: List = plist(pmat, sizes)
    B: List = plist(pmat, sizes)
    Q: List = plist(pmat, sizes)
    R: List = plist(pmat, sizes)
    P: List = plist(pmat, sizes)

    fact: pmat = pmat(nx, nx)

    def factorize(self) -> None:
        M: pmat = pmat(nxu, nxu)
        Mxx: pmat = pmat(nx, nx)
        L: pmat = pmat(nxu, nxu)
        Q: pmat = pmat(nx, nx)
        R: pmat = pmat(nu, nu)
        BA: pmat = pmat(nx, nxu)
        BAtP: pmat = pmat(nxu, nx)
        pmat_copy(self.Q[N-1], self.P[N-1])

        pmat_hcat(self.B[N-1], self.A[N-1], BA)
        pmat_copy(self.Q[N-1], Q)
        pmat_copy(self.R[N-1], R)
        for i in range(1, N):
            pmat_fill(BAtP, 0.0)
            pmt_gemm_tn(BA, self.P[N-i], BAtP, BAtP)

            pmat_fill(M, 0.0)
            M[0:nu,0:nu] = R
            M[nu:nu+nx,nu:nu+nx] = Q

            pmt_gemm_nn(BAtP, BA, M, M)
            pmat_fill(L, 0.0)
            pmt_potrf(M, L)

            Mxx[0:nx, 0:nx] = L[nu:nu+nx, nu:nu+nx]

            # pmat_fill(self.P[N-i-1], 0.0)
            pmt_gemm_nt(Mxx, Mxx, self.P[N-i-1], self.P[N-i-1])
            # pmat_print(self.P[N-i-1])

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
