from prometeo import *

# Gauss-Newton SQP for a cart-pole optimal control problem, with a Riccati
# recursion as QP solver, used for closed-loop MPC (real-time iterations).
#
#   min  sum_k 1/2 (x_k' Q x_k + u_k' R u_k) + 1/2 x_N' Q x_N
#   s.t. x_0 = x0,  x_{k+1} = F(x_k, u_k),  k = 0, ..., N-1
#
# where F is one RK4 step of the cart-pole dynamics. F and its Jacobians are
# CasADi functions, defined in a pure Python block and transpiled with CasADi's
# code generator.

nx : dims = 4
nu : dims = 1
N : dims = 20

# trajectories and stage-wise matrices
x_sizes : dimv = [[nx, 1]] * (N + 1)
u_sizes : dimv = [[nu, 1]] * N
A_sizes : dimv = [[nx, nx]] * N
B_sizes : dimv = [[nx, nu]] * N
b_sizes : dimv = [[nx, 1]] * N
K_sizes : dimv = [[nu, nx]] * N

# model: cart mass, pole mass, pole length, gravity; integration step
M : float = 1.0
m : float = 0.1
l : float = 0.8
g : float = 9.81
h : float = 0.05

n_sqp : int = 30
tol : float = 1e-10
n_mpc : int = 30


# pure >
import casadi as ca

def cartpole_rk4():
    # one RK4 step of the cart-pole dynamics, with its Jacobians computed by CasADi
    x = ca.SX.sym('x', nx)
    u = ca.SX.sym('u', nu)

    def f(x, u):
        th, om = x[1], x[3]
        s, c = ca.sin(th), ca.cos(th)
        d = M + m - m * c * c
        return ca.vertcat(x[2], om,
            (-m * l * s * om * om + m * g * c * s + u[0]) / d,
            (-m * l * c * s * om * om + u[0] * c + (M + m) * g * s) / (l * d))

    k1 = f(x, u)
    k2 = f(x + h / 2 * k1, u)
    k3 = f(x + h / 2 * k2, u)
    k4 = f(x + h * k3, u)
    xnext = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ca.Function('rk4', [x, u], [xnext, ca.jacobian(xnext, x), ca.jacobian(xnext, u)])

# rk4(x, u, xnext, A, B): xnext = F(x, u), A = dF/dx, B = dF/du
rk4 = casadi_function(cartpole_rk4())
# pure <


class SQP:
    def __init__(self) -> None:
        self.xs : List = plist(pmat, x_sizes)
        self.us : List = plist(pmat, u_sizes)
        self.A : List = plist(pmat, A_sizes)
        self.B : List = plist(pmat, B_sizes)
        self.b : List = plist(pmat, b_sizes)
        self.K : List = plist(pmat, K_sizes)
        self.kk : List = plist(pmat, u_sizes)
        self.x0 : pmat = pmat(nx, 1)
        self.Q : pmat = pmat(nx, nx)
        self.R : pmat = pmat(nu, nu)
        self.Q[0, 0] = 10.0
        self.Q[1, 1] = 10.0
        self.Q[2, 2] = 0.1
        self.Q[3, 3] = 0.1
        self.R[0, 0] = 0.1

    def linearize(self) -> None:
        # A_k, B_k and the gaps b_k = F(x_k, u_k) - x_{k+1}
        for k in range(N):
            rk4(self.xs[k], self.us[k], self.b[k], self.A[k], self.B[k])
            pmt_gead(-1.0, self.xs[k + 1], self.b[k])
        return

    def riccati(self) -> None:
        P : pmat = pmat(nx, nx)
        p : pmat = pmat(nx, 1)
        Pn : pmat = pmat(nx, nx)
        PA : pmat = pmat(nx, nx)
        PB : pmat = pmat(nx, nu)
        Pb : pmat = pmat(nx, 1)
        Huu : pmat = pmat(nu, nu)
        L : pmat = pmat(nu, nu)
        Hux : pmat = pmat(nu, nx)
        hu : pmat = pmat(nu, 1)
        pmat_copy(self.Q, P)
        pmt_gemm(self.Q, self.xs[N], p)
        for k in range(N - 1, -1, -1):
            # Pb = p + P b_k
            pmat_copy(p, Pb)
            pmt_gemm_nn(P, self.b[k], Pb, Pb)
            # Huu = R + B' P B, Hux = B' P A, hu = R u + B' Pb
            pmt_gemm(P, self.B[k], PB)
            pmat_copy(self.R, Huu)
            pmt_gemm_tn(self.B[k], PB, Huu, Huu)
            pmt_gemm(P, self.A[k], PA)
            pmat_fill(Hux, 0.0)
            pmt_gemm_tn(self.B[k], PA, Hux, Hux)
            pmt_gemm(self.R, self.us[k], hu)
            pmt_gemm_tn(self.B[k], Pb, hu, hu)
            # K = -Huu^-1 Hux, kk = -Huu^-1 hu
            pmt_potrf(Huu, L)
            pmat_copy(Hux, self.K[k])
            pmt_potrsm(L, self.K[k])
            pmat_copy(hu, self.kk[k])
            pmt_potrsm(L, self.kk[k])
            for j in range(nx):
                self.K[k][0, j] = -self.K[k][0, j]
            self.kk[k][0, 0] = -self.kk[k][0, 0]
            # p = Q x_k + A' Pb + Hux' kk, P = Q + A' P A + Hux' K
            pmt_gemm(self.Q, self.xs[k], p)
            pmt_gemm_tn(self.A[k], Pb, p, p)
            pmt_gemm_tn(Hux, self.kk[k], p, p)
            pmat_copy(self.Q, Pn)
            pmt_gemm_tn(self.A[k], PA, Pn, Pn)
            pmt_gemm_tn(Hux, self.K[k], Pn, Pn)
            pmat_copy(Pn, P)
        return

    def forward(self) -> float:
        # apply the step and return its largest component
        dx : pmat = pmat(nx, 1)
        du : pmat = pmat(nu, 1)
        dxn : pmat = pmat(nx, 1)
        step : float = 0.0
        pmat_copy(self.x0, dx)
        pmt_gead(-1.0, self.xs[0], dx)
        for k in range(N):
            pmat_copy(self.kk[k], du)
            pmt_gemm_nn(self.K[k], dx, du, du)
            pmt_gead(1.0, dx, self.xs[k])
            pmt_gead(1.0, du, self.us[k])
            for i in range(nx):
                step = max(step, abs(dx[i, 0]))
            step = max(step, abs(du[0, 0]))
            pmat_copy(self.b[k], dxn)
            pmt_gemm_nn(self.A[k], dx, dxn, dxn)
            pmt_gemm_nn(self.B[k], du, dxn, dxn)
            pmat_copy(dxn, dx)
        pmt_gead(1.0, dx, self.xs[N])
        for i in range(nx):
            step = max(step, abs(dx[i, 0]))
        return step

    def iterate(self) -> float:
        self.linearize()
        self.riccati()
        return self.forward()


def main() -> int:
    sqp : SQP = SQP()
    step : float = 0.0
    u0 : float = 0.0
    sqp.x0[1, 0] = 0.4

    # solve the OCP from the initial state
    for it in range(n_sqp):
        step = sqp.iterate()
        if step < tol:
            break
    print('converged: step %e\n' % step)
    for k in range(N):
        u0 = sqp.us[k][0, 0]
        print('u = %.10f\n' % u0)

    # closed loop: one SQP iteration per sampling time
    xplant : pmat = pmat(nx, 1)
    xnext : pmat = pmat(nx, 1)
    Aplant : pmat = pmat(nx, nx)
    Bplant : pmat = pmat(nx, nu)
    pmat_copy(sqp.x0, xplant)
    for t in range(n_mpc):
        pmat_copy(xplant, sqp.x0)
        step = sqp.iterate()
        rk4(xplant, sqp.us[0], xnext, Aplant, Bplant)
        pmat_copy(xnext, xplant)
    print('closed-loop state after %i steps:\n' % n_mpc)
    pmat_print(xplant)
    return 0
