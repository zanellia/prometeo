from prometeo import *

# The SQP for MPC of sqp_mpc.py on a larger system: a chain of n_free point
# masses connected by springs, with one end fixed at the origin and the
# velocity of the other end as control input (the "hanging chain" benchmark).
# The state collects the positions of the free masses, the position of the
# controlled end and the velocities of the free masses: nx = 6 n_free + 3.
# The chain starts at rest but with all free masses pushed sideways, and the
# controller brings it back to rest, with bounds on the end velocity.
#
#   min  sum_k 1/2 (x_k' Q x_k + u_k' R u_k) + 1/2 x_N' Q x_N
#   s.t. x_0 = x0,  x_{k+1} = F(x_k, u_k),  u_min <= u_k <= u_max
#
# where x is the deviation from the rest position and F is one RK4 step. The
# rest position (a nonlinear equation) and F with its Jacobians are computed
# by CasADi in a pure Python block.

n_free : dims = 3
nx : dims = 6 * n_free + 3
nu : dims = 3
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

# model: mass, spring constant, rest length of the springs, gravity; position
# of the controlled end at rest; integration step
m : float = 0.033
D : float = 1.0
L0 : float = 0.033
g : float = 9.81
p_end : float = 1.0
h : float = 0.1

# cost: weights of positions, velocities and inputs
q_pos : float = 1.0
q_vel : float = 0.1
r_u : float = 0.01

# bounds on the velocity of the controlled end
u_min : float = -1.0
u_max : float = 1.0

n_sqp : int = 30
tol : float = 1e-10
n_mpc : int = 30

# interior-point method: iterations, tolerance
n_ipm : int = 50
ipm_tol : float = 1e-12


# pure >
import casadi as ca

def chain_rk4():
    # one RK4 step of the chain dynamics in deviation from the rest position,
    # with its Jacobians computed by CasADi
    def f(x, u):
        p = [ca.DM.zeros(3)] + [x[3 * i:3 * i + 3] for i in range(n_free + 1)]
        v = x[3 * n_free + 3:]
        forces = []
        for j in range(n_free + 1):
            d = p[j + 1] - p[j]
            forces.append(D * (1 - L0 / ca.norm_2(d)) * d)
        acc = [(forces[i + 1] - forces[i]) / m - ca.vertcat(0, 0, g) for i in range(n_free)]
        return ca.vertcat(v, u, *acc)

    # rest position of the free masses for the controlled end at (p_end, 0, 0)
    end = ca.DM([p_end, 0, 0])
    z = ca.SX.sym('z', 3 * n_free)
    xz = ca.vertcat(z, end, ca.DM.zeros(3 * n_free))
    residual = ca.Function('residual', [z], [f(xz, ca.DM.zeros(nu))[3 * n_free + 3:]])
    guess = ca.vertcat(*[end * (i + 1) / (n_free + 1) for i in range(n_free)])
    rest = ca.vertcat(ca.rootfinder('rest', 'newton', residual)(guess), end, ca.DM.zeros(3 * n_free))

    x = ca.SX.sym('x', nx)
    u = ca.SX.sym('u', nu)
    y = x + rest
    k1 = f(y, u)
    k2 = f(y + h / 2 * k1, u)
    k3 = f(y + h / 2 * k2, u)
    k4 = f(y + h * k3, u)
    xnext = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ca.Function('rk4', [x, u], [xnext, ca.jacobian(xnext, x), ca.jacobian(xnext, u)])

# rk4(x, u, xnext, A, B): xnext = F(x, u), A = dF/dx, B = dF/du
rk4 = casadi_function(chain_rk4())
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
        for i in range(3 * n_free + 3):
            self.Q[i, i] = q_pos
        for i in range(3 * n_free + 3, nx):
            self.Q[i, i] = q_vel
        for i in range(nu):
            self.R[i, i] = r_u

    def linearize(self) -> None:
        # A_k, B_k and the gaps b_k = F(x_k, u_k) - x_{k+1}
        for k in range(N):
            rk4(self.xs[k], self.us[k], self.b[k], self.A[k], self.B[k])
            pmt_gead(-1.0, self.xs[k + 1], self.b[k])
        return

    def lq_factor(self) -> None:
        # Riccati factorization of the LQ problem
        #   min sum_k 1/2 dx' Q dx + (Q x_k)' dx + 1/2 du' Rt_k du + rt_k' du
        #   s.t. dx_0 = x0 - x_0, dx_{k+1} = A_k dx_k + B_k du_k + b_k
        # P_k, L_k = chol(Rt_k + B_k' P_{k+1} B_k), Hux_k = B_k' P_{k+1} A_k,
        # K_k = -(L_k L_k')^-1 Hux_k
        PA : pmat = pmat(nx, nx)
        PB : pmat = pmat(nx, nu)
        Huu : pmat = pmat(nu, nu)
        pmat_copy(self.Q, self.P[N])
        for k in range(N - 1, -1, -1):
            pmt_gemm(self.P[k + 1], self.B[k], PB)
            pmat_copy(self.Rt[k], Huu)
            pmt_gemm_tn(self.B[k], PB, Huu, Huu)
            pmt_gemm(self.P[k + 1], self.A[k], PA)
            pmat_fill(self.Hux[k], 0.0)
            pmt_gemm_tn(self.B[k], PA, self.Hux[k], self.Hux[k])
            pmt_potrf(Huu, self.L[k])
            pmat_copy(self.Hux[k], self.K[k])
            pmt_potrsm(self.L[k], self.K[k])
            for i in range(nu):
                for j in range(nx):
                    self.K[k][i, j] = -self.K[k][i, j]
            pmat_copy(self.Q, self.P[k])
            pmt_gemm_tn(self.A[k], PA, self.P[k], self.P[k])
            pmt_gemm_tn(self.Hux[k], self.K[k], self.P[k], self.P[k])
        return

    def lq_solve(self) -> None:
        # solution dxn, dun of the factorized LQ problem with gradients rt
        p : pmat = pmat(nx, 1)
        Pb : pmat = pmat(nx, 1)
        hu : pmat = pmat(nu, 1)
        pmt_gemm(self.Q, self.xs[N], p)
        for k in range(N - 1, -1, -1):
            # Pb = p + P b_k, kk = -(L L')^-1 (rt + B' Pb), p = Q x_k + A' Pb + Hux' kk
            pmat_copy(p, Pb)
            pmt_gemm_nn(self.P[k + 1], self.b[k], Pb, Pb)
            pmat_copy(self.rt[k], hu)
            pmt_gemm_tn(self.B[k], Pb, hu, hu)
            pmat_copy(hu, self.kk[k])
            pmt_potrsm(self.L[k], self.kk[k])
            for i in range(nu):
                self.kk[k][i, 0] = -self.kk[k][i, 0]
            pmt_gemm(self.Q, self.xs[k], p)
            pmt_gemm_tn(self.A[k], Pb, p, p)
            pmt_gemm_tn(self.Hux[k], self.kk[k], p, p)
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

    def rhs(self) -> None:
        # gradients rt of the Newton step for the complementarity targets
        # sl * zl = tl, su * zu = tu
        for k in range(N):
            pmt_gemm(self.R, self.us[k], self.rt[k])
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
                pmt_gead(alpha, self.ddu[k], self.du[k])
                pmt_gead(alpha, self.dsl[k], self.sl[k])
                pmt_gead(alpha, self.dsu[k], self.su[k])
                pmt_gead(alpha, self.dzl[k], self.zl[k])
                pmt_gead(alpha, self.dzu[k], self.zu[k])
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
    # push the free masses sideways
    for i in range(n_free):
        sqp.x0[3 * n_free + 3 + 3 * i + 1, 0] = 1.0

    # solve the OCP from the initial state
    for it in range(n_sqp):
        step = sqp.iterate()
        if step < tol:
            break
    print('converged: step %e\n' % step)
    print('interior-point iterations in the last QP: %i\n' % sqp.ipm_iterations)
    for k in range(N):
        for i in range(nu):
            u0 = sqp.us[k][i, 0]
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
