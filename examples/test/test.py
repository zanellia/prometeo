from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims  = 2
nxu: dims = 4
nu: dims  = 2
N:  dims  = 5
n: dims = 10

class qp_data:
    A: List = plist(pmat, sizes)
    B: List = plist(pmat, sizes)
    Q: List = plist(pmat, sizes)
    R: List = plist(pmat, sizes)
    P: List = plist(pmat, sizes)

    fact: List = plist(pmat, sizes)

    def factorize(self) -> None:
        M: pmat = pmat(nxu, nxu)
        Mu: pmat = pmat(nu, nu)
        Mxut: pmat = pmat(nu, nxu)
        Mxx: pmat = pmat(nx, nx)
        Mxu: pmat = pmat(nxu, nu)
        Lu: pmat = pmat(nu, nu)
        Lxu: pmat = pmat(nxu, nxu)
        Q: pmat = pmat(nx, nx)
        R: pmat = pmat(nu, nu)
        BA: pmat = pmat(nx, nxu)
        BAtP: pmat = pmat(nxu, nx)
        pmat_copy(self.Q[N-1], self.P[N-1])
        for i in range(1, N):
            pmat_hcat(self.B[N-i], self.A[N-i], BA)
            pmt_gemm_tn(BA, self.P[N-i], BAtP, BAtP)

            pmat_copy(self.Q[N-i], Q)
            pmat_copy(self.R[N-i], R)
            # M[0:nu,0:nu] = R[0:nu,0:nu]
            M[0:nu,0:nu] = R
            M[nu:nu+nx,nu:nu+nx] = Q

            # this is still not implemented!
            # R = M[0:nu,0:nu]

            for j in range(nu):
                for k in range(nu):
                    M[j,k] = R[j,k]
            for j in range(nx):
                for k in range(nx):
                    M[nu+j,nu+k] = Q[j,k]

            pmt_gemm_nn(BAtP, BA, M, M)
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
            pmt_gemm_nn(Mxut, Mxu, self.P[N-i-1], self.P[N-i-1])
            pmt_gead(-1.0, self.P[N-i-1], Mxx)
            pmat_copy(Mxx, self.P[N-i-1])
            pmat_print(self.P[N-i-1])

        return

def main() -> int:

    # test assignments
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
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.0
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
