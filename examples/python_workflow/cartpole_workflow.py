from prometeo import *

# Developing an algorithm in Python before transpiling it: a Gauss-Newton SQP
# (with Riccati recursions for the QPs) stabilizing a cart-pole, used for
# closed-loop MPC.
#
# The pure blocks below are plain Python: they run with
# 'pmt cartpole_workflow.py' and are removed with
# 'pmt cartpole_workflow.py --cgen=True'. Here they
#   - check intermediate results with NumPy and SciPy (np.array(A) converts a
#     matrix or a vector),
#   - compare the solution with an independent one computed by IPOPT,
#   - log the iterations and the closed loop and plot them with matplotlib,
#   - stop in the debugger (pdb) when a check fails, or with PMT_DEBUG=1.
# The transpiled program computes the same numbers, without any of this.
# See README.md.

nx : dims = 4
nu : dims = 1
N : dims = 20

x_sizes : dimv = [[nx, 1]] * (N + 1)
u_sizes : dimv = [[nu, 1]] * N
A_sizes : dimv = [[nx, nx]] * N
B_sizes : dimv = [[nx, nu]] * N
K_sizes : dimv = [[nu, nx]] * N
R_sizes : dimv = [[nu, nu]] * N
P_sizes : dimv = [[nx, nx]] * (N + 1)

h : float = 0.05
n_sqp : int = 20
tol : float = 1e-10
n_mpc : int = 60
n_dare : int = 300


# pure >
import os
import sys
import numpy as np
import casadi as ca

# PMT_DEBUG=1 pmt cartpole_workflow.py stops in pdb after the first solve
DEBUG = os.environ.get('PMT_DEBUG') == '1'
# what the program does, for the plots: filled by the pure blocks below
log = {'step': [], 'x': [], 'u': [], 'prediction': []}


def cartpole_dynamics():
    x, u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
    M, m, l, g = 1.0, 0.1, 0.8, 9.81
    s, c = ca.sin(x[1]), ca.cos(x[1])
    d = M + m - m * c * c
    f = ca.vertcat(x[2], x[3], (-m * l * s * x[3] ** 2 + m * g * c * s + u[0]) / d,
        (-m * l * c * s * x[3] ** 2 + u[0] * c + (M + m) * g * s) / (l * d))
    return ca.Function('f', [x, u], [f])


def cartpole_rk4():
    # one RK4 step and its Jacobians, computed by CasADi
    f = cartpole_dynamics()
    x, u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
    k1 = f(x, u)
    k2 = f(x + h / 2 * k1, u)
    k3 = f(x + h / 2 * k2, u)
    k4 = f(x + h * k3, u)
    xn = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ca.Function('rk4', [x, u], [xn, ca.jacobian(xn, x), ca.jacobian(xn, u)])


def ipopt_solution(x0, Q, R, QN):
    # the same optimal control problem, solved by IPOPT
    F = cartpole_rk4()
    opti = ca.Opti()
    X, U = opti.variable(nx, N + 1), opti.variable(nu, N)
    cost = 0
    for k in range(N):
        cost += 0.5 * (ca.bilin(Q, X[:, k], X[:, k]) + ca.bilin(R, U[:, k], U[:, k]))
        opti.subject_to(X[:, k + 1] == F(X[:, k], U[:, k])[0])
    opti.minimize(cost + 0.5 * ca.bilin(QN, X[:, N], X[:, N]))
    opti.subject_to(X[:, 0] == x0)
    opti.solver('ipopt', {'print_time': False}, {'print_level': 0, 'sb': 'yes', 'tol': 1e-12})
    return np.array(opti.solve().value(U)).reshape(N, nu)


rk4 = casadi_function(cartpole_rk4())
# pure <


class SQP:
    def __init__(self) -> None:
        self.xs : List = plist(pmat, x_sizes)
        self.us : List = plist(pmat, u_sizes)
        self.A : List = plist(pmat, A_sizes)
        self.B : List = plist(pmat, B_sizes)
        self.b : List = plist(pmat, x_sizes)
        self.P : List = plist(pmat, P_sizes)
        self.L : List = plist(pmat, R_sizes)
        self.K : List = plist(pmat, K_sizes)
        self.Hux : List = plist(pmat, K_sizes)
        self.kk : List = plist(pmat, u_sizes)
        self.dx : List = plist(pmat, x_sizes)
        self.du : List = plist(pmat, u_sizes)
        self.x0 : pmat = pmat(nx, 1)
        self.Q : pmat = pmat(nx, nx)
        self.R : pmat = pmat(nu, nu)
        self.QN : pmat = pmat(nx, nx)
        self.Q[0, 0] = 10.0
        self.Q[1, 1] = 10.0
        self.Q[2, 2] = 0.1
        self.Q[3, 3] = 0.1
        self.R[0, 0] = 0.1

    def terminal_cost(self) -> None:
        # QN: the LQR cost-to-go of the dynamics linearized at the upright
        # position (the discrete-time algebraic Riccati equation, solved by
        # iterating the Riccati recursion)
        x : pmat = pmat(nx, 1)
        u : pmat = pmat(nu, 1)
        xn : pmat = pmat(nx, 1)
        A : pmat = pmat(nx, nx)
        B : pmat = pmat(nx, nu)
        PA : pmat = pmat(nx, nx)
        L : pmat = pmat(nu, nu)
        K : pmat = pmat(nu, nx)
        rk4(x, u, xn, A, B)
        pmat_copy(self.Q, self.QN)
        for it in range(n_dare):
            PA = self.QN @ A
            L = cholesky(self.R + B.T @ self.QN @ B)
            K = -cho_solve(L, B.T @ PA)
            self.QN = self.Q + A.T @ PA + PA.T @ B @ K
            # the recursion does not preserve symmetry: without this, rounding
            # errors grow with the unstable mode and QN diverges (to NaN after
            # about 250 iterations: the check in riccati found it)
            self.QN = 0.5 * (self.QN + self.QN.T)
        # pure >
        # check against SciPy's solver of the Riccati equation
        import scipy.linalg
        P = scipy.linalg.solve_discrete_are(np.array(A), np.array(B), np.array(self.Q), np.array(self.R))
        print('[python] terminal cost, difference from scipy: {:.1e}'.format(
            np.abs(np.array(self.QN) - P).max() / np.abs(P).max()))
        # pure <
        return

    def linearize(self) -> None:
        # A_k, B_k and the gaps b_k = F(x_k, u_k) - x_{k+1}
        for k in range(N):
            rk4(self.xs[k], self.us[k], self.b[k], self.A[k], self.B[k])
            self.b[k] -= self.xs[k + 1]
        return

    def riccati(self) -> None:
        # Newton step: min sum 1/2 dx'Q dx + (Q x_k)'dx + 1/2 du'R du + (R u_k)'du
        # (with QN instead of Q at the last stage)
        # s.t. dx_0 = x0 - x_0, dx_{k+1} = A_k dx_k + B_k du_k + b_k
        PA : pmat = pmat(nx, nx)
        PB : pmat = pmat(nx, nu)
        p : pmat = pmat(nx, 1)
        Pb : pmat = pmat(nx, 1)
        pmat_copy(self.QN, self.P[N])
        p = self.QN @ self.xs[N]
        for k in range(N - 1, -1, -1):
            PA = self.P[k + 1] @ self.A[k]
            PB = self.P[k + 1] @ self.B[k]
            Pb = p + self.P[k + 1] @ self.b[k]
            self.Hux[k] = self.B[k].T @ PA
            self.L[k] = cholesky(self.R + self.B[k].T @ PB)
            self.K[k] = -cho_solve(self.L[k], self.Hux[k])
            self.kk[k] = -cho_solve(self.L[k], self.R @ self.us[k] + self.B[k].T @ Pb)
            self.P[k] = self.Q + self.A[k].T @ PA + self.Hux[k].T @ self.K[k]
            p = self.Q @ self.xs[k] + self.A[k].T @ Pb + self.Hux[k].T @ self.kk[k]
            # pure >
            # the cost-to-go matrices must be symmetric positive definite
            P = np.array(self.P[k])
            if np.abs(P - P.T).max() > 1e-8 * np.abs(P).max() or np.linalg.eigvalsh(P).min() <= 0:
                print('P[{}] is not symmetric positive definite:\n{}'.format(k, P))
                breakpoint()
            # pure <
        self.dx[0] = self.x0 - self.xs[0]
        for k in range(N):
            self.du[k] = self.K[k] @ self.dx[k] + self.kk[k]
            self.dx[k + 1] = self.A[k] @ self.dx[k] + self.B[k] @ self.du[k] + self.b[k]
        return

    def iterate(self) -> float:
        # one SQP iteration; returns the largest component of the step
        step : float = 0.0
        self.linearize()
        self.riccati()
        for k in range(N):
            step = max(step, abs(self.du[k][0, 0]))
            self.us[k] += self.du[k]
        for k in range(N + 1):
            for i in range(nx):
                step = max(step, abs(self.dx[k][i, 0]))
            self.xs[k] += self.dx[k]
        # pure >
        log['step'].append(step)
        # pure <
        return step

    def shift(self) -> None:
        # warm start for the next sampling time: the solution shifted by one
        # stage (the last stage is repeated)
        for k in range(N - 1):
            pmat_copy(self.us[k + 1], self.us[k])
        for k in range(N):
            pmat_copy(self.xs[k + 1], self.xs[k])
        return


def main() -> int:
    sqp : SQP = SQP()
    step : float = 0.0
    iterations : int = 0
    sqp.x0[1, 0] = 0.4
    sqp.terminal_cost()

    # solve the optimal control problem from x0
    for it in range(n_sqp):
        step = sqp.iterate()
        iterations = iterations + 1
        if step < tol:
            break
    print('first solve: %i SQP iterations\n' % iterations)

    # pure >
    # compare with IPOPT: same problem, independent solver
    u = np.array([np.array(sqp.us[k])[0, 0] for k in range(N)])
    u_ipopt = ipopt_solution(np.array(sqp.x0).flatten(), np.array(sqp.Q), np.array(sqp.R),
        np.array(sqp.QN))
    print('[python] difference from IPOPT: {:.1e}'.format(np.abs(u - u_ipopt[:, 0]).max()))
    assert np.allclose(u, u_ipopt[:, 0], atol=1e-8)
    if DEBUG:
        # inspect anything, e.g. np.array(sqp.K[0]), np.array(sqp.P[0]), log['step']
        breakpoint()
    # pure <

    # closed loop: one SQP iteration (real-time iteration) per sampling time
    xplant : pmat = pmat(nx, 1)
    A : pmat = pmat(nx, nx)
    B : pmat = pmat(nx, nu)
    pmat_copy(sqp.x0, xplant)
    for t in range(n_mpc):
        pmat_copy(xplant, sqp.x0)
        step = sqp.iterate()
        rk4(xplant, sqp.us[0], xplant, A, B)
        # pure >
        log['x'].append(np.array(xplant).flatten())
        log['u'].append(np.array(sqp.us[0])[0, 0])
        log['prediction'].append(np.array([np.array(x).flatten() for x in sqp.xs]))
        # pure <
        sqp.shift()
    print('closed loop: final angle %f\n' % xplant[1, 0])

    # pure >
    # in a terminal, an interactive figure (if there is a display); when the
    # output is redirected (e.g. in the tests), the figure is only saved
    interactive = sys.stdout.isatty()
    try:
        import matplotlib
        if not interactive:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Slider
    except ImportError:
        print('[python] matplotlib is not installed: no plots')
        return 0
    # the closed loop from x0, and the prediction made at each sampling time
    t = h * np.arange(n_mpc + 1)
    x = np.array([np.array([0.0, 0.4, 0.0, 0.0])] + log['x'])
    fig, ax = plt.subplots(3, 1, figsize=(7, 9))
    ax[0].plot(t, x[:, 0], label='cart position')
    ax[0].plot(t, x[:, 1], label='pole angle')
    ax[0].set_xlabel('time [s]')
    ax[0].legend()
    ax[1].step(t[:-1], log['u'], where='post')
    ax[1].set_xlabel('time [s]')
    ax[1].set_ylabel('force')
    ax[2].step(np.arange(len(log['step'])), log['step'], where='post')
    ax[2].set_yscale('log')
    ax[2].set_xlabel('SQP iteration (first solve, then one per sampling time)')
    ax[2].set_ylabel('step size')
    for a in ax:
        a.grid(True, alpha=0.4)
    fig.tight_layout()
    fig.savefig('cartpole_workflow.png')
    print('[python] plots saved to cartpole_workflow.png')
    if interactive and matplotlib.get_backend().lower() != 'agg':
        # a slider to go through the sampling times: the prediction made at
        # each one (dashed, with markers) and its SQP iteration
        fig.subplots_adjust(bottom=0.12)
        predicted = [ax[0].plot([], [], '--o', color=c, lw=1.2, ms=3.5, mfc='white', zorder=3)[0]
            for c in ('C0', 'C1')]
        start = [ax[0].plot([], [], 'o', color=c, ms=9, zorder=4)[0] for c in ('C0', 'C1')]
        ax[0].plot([], [], '--o', color='gray', lw=1.2, ms=3.5, mfc='white',
            label='prediction at the selected time')
        ax[0].legend()
        now = [a.axvline(0.0, color='k', lw=0.8) for a in ax[:2]]
        current, = ax[2].plot([], [], 'o', color='C3', markersize=9)
        slider = Slider(fig.add_axes([0.2, 0.02, 0.6, 0.03]), 'sampling time', 0, n_mpc - 1,
            valinit=0, valstep=1)

        def show(k):
            k = int(k)
            for i, line in enumerate(predicted):
                line.set_data(t[k] + h * np.arange(N + 1), log['prediction'][k][:, i])
                start[i].set_data([t[k]], [log['prediction'][k][0, i]])
            for line in now:
                line.set_xdata([t[k], t[k]])
            current.set_data([iterations + k], [log['step'][iterations + k]])
            fig.canvas.draw_idle()

        slider.on_changed(show)
        show(0)
        print('[python] close the figure to continue')
        plt.show()
    # pure <
    return 0
