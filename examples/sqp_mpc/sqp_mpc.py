from prometeo import *

# Gauss-Newton SQP for a cart-pole optimal control problem with input bounds,
# used for closed-loop MPC (real-time iterations). The QPs are solved by a
# primal-dual interior-point method, whose Newton steps are Riccati recursions.
#
#   min  sum_k 1/2 (x_k' Q x_k + u_k' R u_k) + 1/2 x_N' Q x_N
#   s.t. x_0 = x0,  x_{k+1} = F(x_k, u_k),  u_min <= u_k <= u_max
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
R_sizes : dimv = [[nu, nu]] * N

# model: cart mass, pole mass, pole length, gravity; integration step
M : float = 1.0
m : float = 0.1
l : float = 0.8
g : float = 9.81
h : float = 0.05

# input bounds
u_min : float = -5.0
u_max : float = 5.0

n_sqp : int = 30
tol : float = 1e-10
n_mpc : int = 30

# interior-point method: iterations, tolerance, centering parameter
n_ipm : int = 50
ipm_tol : float = 1e-12
sigma : float = 0.1


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
        # iterate and linearization
        self.xs : List = plist(pmat, x_sizes)
        self.us : List = plist(pmat, u_sizes)
        self.A : List = plist(pmat, A_sizes)
        self.B : List = plist(pmat, B_sizes)
        self.b : List = plist(pmat, b_sizes)
        # QP: step, its bounds, slacks and multipliers of the bounds
        self.dx : List = plist(pmat, x_sizes)
        self.du : List = plist(pmat, u_sizes)
        self.lb : List = plist(pmat, u_sizes)
        self.ub : List = plist(pmat, u_sizes)
        self.sl : List = plist(pmat, u_sizes)
        self.su : List = plist(pmat, u_sizes)
        self.zl : List = plist(pmat, u_sizes)
        self.zu : List = plist(pmat, u_sizes)
        # Newton step of the interior-point method: an LQ problem with
        # modified input Hessians Rt and gradients rt, solution dxn, dun
        self.Rt : List = plist(pmat, R_sizes)
        self.rt : List = plist(pmat, u_sizes)
        self.K : List = plist(pmat, K_sizes)
        self.kk : List = plist(pmat, u_sizes)
        self.dxn : List = plist(pmat, x_sizes)
        self.dun : List = plist(pmat, u_sizes)
        self.x0 : pmat = pmat(nx, 1)
        self.Q : pmat = pmat(nx, nx)
        self.R : pmat = pmat(nu, nu)
        self.ipm_iterations : int = 0
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

    def lq(self) -> None:
        # min sum_k 1/2 dx' Q dx + (Q x_k)' dx + 1/2 du' Rt_k du + rt_k' du
        # s.t. dx_0 = x0 - x_0, dx_{k+1} = A_k dx_k + B_k du_k + b_k
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
            # Huu = Rt + B' P B, Hux = B' P A, hu = rt + B' Pb
            pmt_gemm(P, self.B[k], PB)
            pmat_copy(self.Rt[k], Huu)
            pmt_gemm_tn(self.B[k], PB, Huu, Huu)
            pmt_gemm(P, self.A[k], PA)
            pmat_fill(Hux, 0.0)
            pmt_gemm_tn(self.B[k], PA, Hux, Hux)
            pmat_copy(self.rt[k], hu)
            pmt_gemm_tn(self.B[k], Pb, hu, hu)
            # K = -Huu^-1 Hux, kk = -Huu^-1 hu
            pmt_potrf(Huu, L)
            pmat_copy(Hux, self.K[k])
            pmt_potrsm(L, self.K[k])
            pmat_copy(hu, self.kk[k])
            pmt_potrsm(L, self.kk[k])
            for i in range(nu):
                for j in range(nx):
                    self.K[k][i, j] = -self.K[k][i, j]
                self.kk[k][i, 0] = -self.kk[k][i, 0]
            # p = Q x_k + A' Pb + Hux' kk, P = Q + A' P A + Hux' K
            pmt_gemm(self.Q, self.xs[k], p)
            pmt_gemm_tn(self.A[k], Pb, p, p)
            pmt_gemm_tn(Hux, self.kk[k], p, p)
            pmat_copy(self.Q, Pn)
            pmt_gemm_tn(self.A[k], PA, Pn, Pn)
            pmt_gemm_tn(Hux, self.K[k], Pn, Pn)
            pmat_copy(Pn, P)
        # forward: dun_k = K_k dxn_k + kk_k
        pmat_copy(self.x0, self.dxn[0])
        pmt_gead(-1.0, self.xs[0], self.dxn[0])
        for k in range(N):
            pmat_copy(self.kk[k], self.dun[k])
            pmt_gemm_nn(self.K[k], self.dxn[k], self.dun[k], self.dun[k])
            pmat_copy(self.b[k], self.dxn[k + 1])
            pmt_gemm_nn(self.A[k], self.dxn[k], self.dxn[k + 1], self.dxn[k + 1])
            pmt_gemm_nn(self.B[k], self.dun[k], self.dxn[k + 1], self.dxn[k + 1])
        return

    def ipm(self) -> None:
        # QP with bounds lb <= du <= ub: slacks sl = du - lb, su = ub - du,
        # multipliers zl, zu, with sl * zl = su * zu = sigma * mu
        mu : float = 0.0
        res : float = 0.0
        pairs : float = 0.0
        alpha : float = 1.0
        for k in range(N):
            for i in range(nu):
                self.lb[k][i, 0] = u_min - self.us[k][i, 0]
                self.ub[k][i, 0] = u_max - self.us[k][i, 0]
                self.du[k][i, 0] = 0.0
                self.sl[k][i, 0] = 1.0
                self.su[k][i, 0] = 1.0
                self.zl[k][i, 0] = 1.0
                self.zu[k][i, 0] = 1.0
        for it in range(n_ipm):
            self.ipm_iterations = it
            # duality measure and primal residual
            mu = 0.0
            res = 0.0
            pairs = 0.0
            for k in range(N):
                for i in range(nu):
                    mu += self.sl[k][i, 0] * self.zl[k][i, 0] + self.su[k][i, 0] * self.zu[k][i, 0]
                    pairs += 2.0
                    res = max(res, abs(self.du[k][i, 0] - self.lb[k][i, 0] - self.sl[k][i, 0]))
                    res = max(res, abs(self.ub[k][i, 0] - self.du[k][i, 0] - self.su[k][i, 0]))
            mu = mu / pairs
            if mu < ipm_tol and res < ipm_tol:
                break
            # Newton step: LQ problem with modified Hessians and gradients
            for k in range(N):
                pmat_copy(self.R, self.Rt[k])
                pmt_gemm(self.R, self.us[k], self.rt[k])
                for i in range(nu):
                    du : float = self.du[k][i, 0]
                    sl : float = self.sl[k][i, 0]
                    su : float = self.su[k][i, 0]
                    zl : float = self.zl[k][i, 0]
                    zu : float = self.zu[k][i, 0]
                    rl : float = du - self.lb[k][i, 0] - sl
                    ru : float = self.ub[k][i, 0] - du - su
                    D : float = zl / sl + zu / su
                    self.Rt[k][i, i] += D
                    self.rt[k][i, 0] += -D * du - sigma * mu / sl + zl * rl / sl \
                        + sigma * mu / su - zu * ru / su
            self.lq()
            # step length: fraction to the boundary
            alpha = 1.0
            for k in range(N):
                for i in range(nu):
                    ddu : float = self.dun[k][i, 0] - self.du[k][i, 0]
                    dsl : float = ddu + self.du[k][i, 0] - self.lb[k][i, 0] - self.sl[k][i, 0]
                    dsu : float = self.ub[k][i, 0] - self.du[k][i, 0] - self.su[k][i, 0] - ddu
                    dzl : float = (sigma * mu - self.zl[k][i, 0] * (self.sl[k][i, 0] + dsl)) / self.sl[k][i, 0]
                    dzu : float = (sigma * mu - self.zu[k][i, 0] * (self.su[k][i, 0] + dsu)) / self.su[k][i, 0]
                    if dsl < 0.0:
                        alpha = min(alpha, -0.995 * self.sl[k][i, 0] / dsl)
                    if dsu < 0.0:
                        alpha = min(alpha, -0.995 * self.su[k][i, 0] / dsu)
                    if dzl < 0.0:
                        alpha = min(alpha, -0.995 * self.zl[k][i, 0] / dzl)
                    if dzu < 0.0:
                        alpha = min(alpha, -0.995 * self.zu[k][i, 0] / dzu)
            for k in range(N):
                for i in range(nu):
                    ddu : float = self.dun[k][i, 0] - self.du[k][i, 0]
                    dsl : float = ddu + self.du[k][i, 0] - self.lb[k][i, 0] - self.sl[k][i, 0]
                    dsu : float = self.ub[k][i, 0] - self.du[k][i, 0] - self.su[k][i, 0] - ddu
                    dzl : float = (sigma * mu - self.zl[k][i, 0] * (self.sl[k][i, 0] + dsl)) / self.sl[k][i, 0]
                    dzu : float = (sigma * mu - self.zu[k][i, 0] * (self.su[k][i, 0] + dsu)) / self.su[k][i, 0]
                    self.du[k][i, 0] += alpha * ddu
                    self.sl[k][i, 0] += alpha * dsl
                    self.su[k][i, 0] += alpha * dsu
                    self.zl[k][i, 0] += alpha * dzl
                    self.zu[k][i, 0] += alpha * dzu
        return

    def apply(self) -> float:
        # states consistent with the dynamics and the inputs of the QP
        # solution; apply the step and return its largest component
        step : float = 0.0
        pmat_copy(self.x0, self.dx[0])
        pmt_gead(-1.0, self.xs[0], self.dx[0])
        for k in range(N):
            pmat_copy(self.b[k], self.dx[k + 1])
            pmt_gemm_nn(self.A[k], self.dx[k], self.dx[k + 1], self.dx[k + 1])
            pmt_gemm_nn(self.B[k], self.du[k], self.dx[k + 1], self.dx[k + 1])
        for k in range(N):
            for i in range(nu):
                step = max(step, abs(self.du[k][i, 0]))
            pmt_gead(1.0, self.du[k], self.us[k])
        for k in range(N + 1):
            for i in range(nx):
                step = max(step, abs(self.dx[k][i, 0]))
            pmt_gead(1.0, self.dx[k], self.xs[k])
        return step

    def iterate(self) -> float:
        self.linearize()
        self.ipm()
        return self.apply()


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
    print('interior-point iterations in the last QP: %i\n' % sqp.ipm_iterations)
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
