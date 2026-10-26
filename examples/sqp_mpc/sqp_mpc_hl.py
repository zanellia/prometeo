from prometeo import *

# Gauss-Newton SQP for a cart-pole optimal control problem with input bounds,
# used for closed-loop MPC (real-time iterations). The QPs are solved by a
# primal-dual interior-point method (Mehrotra's predictor-corrector), whose
# Newton steps are Riccati recursions.
#
# This is sqp_mpc.py written with matrix expressions (A.T @ P @ A, cholesky,
# cho_solve, ...) instead of explicit calls of the linear algebra routines;
# the two programs compute the same numbers.
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
P_sizes : dimv = [[nx, nx]] * (N + 1)

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

# interior-point method: iterations, tolerance
n_ipm : int = 50
ipm_tol : float = 1e-12


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
        # factorization, reused by the predictor and corrector solves
        self.P : List = plist(pmat, P_sizes)
        self.L : List = plist(pmat, R_sizes)
        self.Hux : List = plist(pmat, K_sizes)
        # targets of the complementarity products sl * zl, su * zu
        self.tl : List = plist(pmat, u_sizes)
        self.tu : List = plist(pmat, u_sizes)
        # search directions
        self.ddu : List = plist(pmat, u_sizes)
        self.dsl : List = plist(pmat, u_sizes)
        self.dsu : List = plist(pmat, u_sizes)
        self.dzl : List = plist(pmat, u_sizes)
        self.dzu : List = plist(pmat, u_sizes)
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
            self.b[k] -= self.xs[k + 1]
        return

    def lq_factor(self) -> None:
        # Riccati factorization of the LQ problem
        #   min sum_k 1/2 dx' Q dx + (Q x_k)' dx + 1/2 du' Rt_k du + rt_k' du
        #   s.t. dx_0 = x0 - x_0, dx_{k+1} = A_k dx_k + B_k du_k + b_k
        PA : pmat = pmat(nx, nx)
        PB : pmat = pmat(nx, nu)
        pmat_copy(self.Q, self.P[N])
        for k in range(N - 1, -1, -1):
            PA = self.P[k + 1] @ self.A[k]
            PB = self.P[k + 1] @ self.B[k]
            self.Hux[k] = self.B[k].T @ PA
            self.L[k] = cholesky(self.Rt[k] + self.B[k].T @ PB)
            self.K[k] = -cho_solve(self.L[k], self.Hux[k])
            self.P[k] = self.Q + self.A[k].T @ PA + self.Hux[k].T @ self.K[k]
        return

    def lq_solve(self) -> None:
        # solution dxn, dun of the factorized LQ problem with gradients rt
        p : pmat = pmat(nx, 1)
        Pb : pmat = pmat(nx, 1)
        p = self.Q @ self.xs[N]
        for k in range(N - 1, -1, -1):
            Pb = p + self.P[k + 1] @ self.b[k]
            self.kk[k] = -cho_solve(self.L[k], self.rt[k] + self.B[k].T @ Pb)
            p = self.Q @ self.xs[k] + self.A[k].T @ Pb + self.Hux[k].T @ self.kk[k]
        self.dxn[0] = self.x0 - self.xs[0]
        for k in range(N):
            self.dun[k] = self.K[k] @ self.dxn[k] + self.kk[k]
            self.dxn[k + 1] = self.A[k] @ self.dxn[k] + self.B[k] @ self.dun[k] + self.b[k]
        return

    def rhs(self) -> None:
        # gradients rt of the Newton step for the complementarity targets
        # sl * zl = tl, su * zu = tu
        for k in range(N):
            self.rt[k] = self.R @ self.us[k]
            for i in range(nu):
                du : float = self.du[k][i, 0]
                sl : float = self.sl[k][i, 0]
                su : float = self.su[k][i, 0]
                zl : float = self.zl[k][i, 0]
                zu : float = self.zu[k][i, 0]
                rl : float = du - self.lb[k][i, 0] - sl
                ru : float = self.ub[k][i, 0] - du - su
                self.rt[k][i, 0] += -(zl / sl + zu / su) * du - self.tl[k][i, 0] / sl \
                    + zl * rl / sl + self.tu[k][i, 0] / su - zu * ru / su
        return

    def directions(self) -> None:
        # search directions from the solution of the Newton step
        for k in range(N):
            for i in range(nu):
                ddu : float = self.dun[k][i, 0] - self.du[k][i, 0]
                dsl : float = ddu + self.du[k][i, 0] - self.lb[k][i, 0] - self.sl[k][i, 0]
                dsu : float = self.ub[k][i, 0] - self.du[k][i, 0] - self.su[k][i, 0] - ddu
                self.ddu[k][i, 0] = ddu
                self.dsl[k][i, 0] = dsl
                self.dsu[k][i, 0] = dsu
                self.dzl[k][i, 0] = (self.tl[k][i, 0] - self.zl[k][i, 0] * (self.sl[k][i, 0] + dsl)) / self.sl[k][i, 0]
                self.dzu[k][i, 0] = (self.tu[k][i, 0] - self.zu[k][i, 0] * (self.su[k][i, 0] + dsu)) / self.su[k][i, 0]
        return

    def max_step(self, frac: float) -> float:
        # largest step in [0, 1] keeping slacks and multipliers positive
        alpha : float = 1.0
        for k in range(N):
            for i in range(nu):
                if self.dsl[k][i, 0] < 0.0:
                    alpha = min(alpha, -frac * self.sl[k][i, 0] / self.dsl[k][i, 0])
                if self.dsu[k][i, 0] < 0.0:
                    alpha = min(alpha, -frac * self.su[k][i, 0] / self.dsu[k][i, 0])
                if self.dzl[k][i, 0] < 0.0:
                    alpha = min(alpha, -frac * self.zl[k][i, 0] / self.dzl[k][i, 0])
                if self.dzu[k][i, 0] < 0.0:
                    alpha = min(alpha, -frac * self.zu[k][i, 0] / self.dzu[k][i, 0])
        return alpha

    def ipm(self) -> None:
        # QP with bounds lb <= du <= ub: slacks sl = du - lb, su = ub - du,
        # multipliers zl, zu; Mehrotra's predictor-corrector method
        mu : float = 0.0
        mu_aff : float = 0.0
        ratio : float = 0.0
        res : float = 0.0
        pairs : float = 0.0
        alpha : float = 1.0
        for k in range(N):
            for i in range(nu):
                self.lb[k][i, 0] = u_min - self.us[k][i, 0]
                self.ub[k][i, 0] = u_max - self.us[k][i, 0]
                self.du[k][i, 0] = 0.0
                # slacks consistent with du = 0 (at least 1)
                self.sl[k][i, 0] = max(-self.lb[k][i, 0], 1.0)
                self.su[k][i, 0] = max(self.ub[k][i, 0], 1.0)
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
            # factorize the Newton system: input Hessians R + zl / sl + zu / su
            for k in range(N):
                pmat_copy(self.R, self.Rt[k])
                for i in range(nu):
                    self.Rt[k][i, i] += self.zl[k][i, 0] / self.sl[k][i, 0] \
                        + self.zu[k][i, 0] / self.su[k][i, 0]
            self.lq_factor()
            # predictor (affine scaling) step: targets 0
            for k in range(N):
                pmat_fill(self.tl[k], 0.0)
                pmat_fill(self.tu[k], 0.0)
            self.rhs()
            self.lq_solve()
            self.directions()
            alpha = self.max_step(1.0)
            mu_aff = 0.0
            for k in range(N):
                for i in range(nu):
                    mu_aff += (self.sl[k][i, 0] + alpha * self.dsl[k][i, 0]) * (self.zl[k][i, 0] + alpha * self.dzl[k][i, 0]) \
                        + (self.su[k][i, 0] + alpha * self.dsu[k][i, 0]) * (self.zu[k][i, 0] + alpha * self.dzu[k][i, 0])
            mu_aff = mu_aff / pairs
            # corrector: centering sigma mu with sigma = (mu_aff / mu)^3, and
            # the second-order term of the predictor
            ratio = mu_aff / mu
            for k in range(N):
                for i in range(nu):
                    self.tl[k][i, 0] = ratio * ratio * ratio * mu - self.dsl[k][i, 0] * self.dzl[k][i, 0]
                    self.tu[k][i, 0] = ratio * ratio * ratio * mu - self.dsu[k][i, 0] * self.dzu[k][i, 0]
            self.rhs()
            self.lq_solve()
            self.directions()
            alpha = self.max_step(max(0.995, 1.0 - mu))
            for k in range(N):
                self.du[k] += alpha * self.ddu[k]
                self.sl[k] += alpha * self.dsl[k]
                self.su[k] += alpha * self.dsu[k]
                self.zl[k] += alpha * self.dzl[k]
                self.zu[k] += alpha * self.dzu[k]
        return

    def apply(self) -> float:
        # states consistent with the dynamics and the inputs of the QP
        # solution; apply the step and return its largest component
        step : float = 0.0
        self.dx[0] = self.x0 - self.xs[0]
        for k in range(N):
            self.dx[k + 1] = self.A[k] @ self.dx[k] + self.B[k] @ self.du[k] + self.b[k]
        for k in range(N):
            for i in range(nu):
                step = max(step, abs(self.du[k][i, 0]))
            self.us[k] += self.du[k]
        for k in range(N + 1):
            for i in range(nx):
                step = max(step, abs(self.dx[k][i, 0]))
            self.xs[k] += self.dx[k]
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
