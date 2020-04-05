from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims  = 2
nxu: dims = 4
nu: dims  = 2
N:  dims  = 5

def function1() -> None:
    # M: pmat = pmat(nxu, nxu)
    function2()
    return
                        
def function2() -> None:
    function1()
    return

class qp_data:
    A: List = plist(pmat, sizes)
    B: List = plist(pmat, sizes)
    Q: List = plist(pmat, sizes)
    R: List = plist(pmat, sizes)
    P: List = plist(pmat, sizes)

    fact: List = plist(pmat, sizes)

    def factorize(self) -> None:
        Qk: pmat = pmat(nx, nx)
        Rk: pmat = pmat(nu, nu)
        Ak: pmat = pmat(nx, nx)
        Bk: pmat = pmat(nu, nu)
        Pk: pmat = pmat(nx, nx)
        pmat_copy(self.Q[N-1], Pk)
        pmat_copy(Pk, self.P[N-1])

        for i in range(1, N):
            pmat_copy(self.Q[N-i-1], Qk)
            pmat_copy(self.R[N-i-1], Rk)
            pmat_copy(self.B[N-i-1], Bk)
            pmat_copy(self.A[N-i-1], Ak)

            pparse('Pk = Qk + Ak.T * Pk * Ak ' \
                '- (Ak.T * Pk * Bk) * ((Rk + Bk.T * Pk * Bk)' \
                '\ (Bk.T * Pk * Ak))')

            pmat_print(Pk)
            pmat_copy(Pk, self.P[N-i-1])

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
