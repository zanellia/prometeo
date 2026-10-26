from prometeo import *

# LQR for a double integrator: Riccati recursion, then a closed-loop simulation

n : dims = 2        # sizes are compile-time constants
m : dims = 1
N : dims = 100

def lqr(A: pmat[n, n], B: pmat[n, m], Q: pmat[n, n], R: pmat[m, m],
        P: pmat[n, n], K: pmat[m, n]) -> None:
    # P = Q + A'P(A + BK), K = -(R + B'PB)^-1 B'PA, iterated N times
    L : pmat = pmat(m, m)
    pmat_copy(Q, P)
    for k in range(N):
        L = cholesky(R + B.T @ P @ B)
        K = -cho_solve(L, B.T @ P @ A)
        P = Q + A.T @ P @ (A + B @ K)
        P = 0.5 * (P + P.T)
    return

def main() -> int:
    A : pmat = pmat(n, n)
    B : pmat = pmat(n, m)
    Q : pmat = pmat(n, n)
    R : pmat = pmat(m, m)
    P : pmat = pmat(n, n)
    K : pmat = pmat(m, n)
    x : pvec = pvec(n)
    h : float = 0.1
    A[0, 0] = 1.0
    A[0, 1] = h
    A[1, 1] = 1.0
    B[1, 0] = h
    Q[0, 0] = 1.0
    Q[1, 1] = 0.1
    R[0, 0] = 0.01

    lqr(A, B, Q, R, P, K)
    pmat_print(K)

    x[0] = 1.0
    print('cost-to-go: %f\n' % (0.5 * (x @ P @ x)))
    for t in range(50):
        x = (A + B @ K) @ x
    print('state after 5 s: %e\n' % x[0])
    return 0
