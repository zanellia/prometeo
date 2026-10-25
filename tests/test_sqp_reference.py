"""Check the SQP example (examples/sqp_mpc) against an independent solution
of the same optimal control problem computed with CasADi and IPOPT."""

import os
import shutil

import casadi as ca
import numpy as np

from pmt_testing import run_pmt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# problem data, as in examples/sqp_mpc/sqp_mpc.py
M, m, l, g = 1.0, 0.1, 0.8, 9.81
nx, nu, N, h = 4, 1, 20, 0.05
Q = np.diag([10.0, 10.0, 0.1, 0.1])
R = np.diag([0.1])
x0 = np.array([0.0, 0.4, 0.0, 0.0])


def ipopt_solution():
    x, u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
    s, c = ca.sin(x[1]), ca.cos(x[1])
    d = M + m - m * c * c
    f = ca.Function('f', [x, u], [ca.vertcat(x[2], x[3],
        (-m * l * s * x[3] ** 2 + m * g * c * s + u[0]) / d,
        (-m * l * c * s * x[3] ** 2 + u[0] * c + (M + m) * g * s) / (l * d))])
    k1 = f(x, u)
    k2 = f(x + h / 2 * k1, u)
    k3 = f(x + h / 2 * k2, u)
    k4 = f(x + h * k3, u)
    F = ca.Function('F', [x, u], [x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)])

    X = ca.SX.sym('X', nx, N + 1)
    U = ca.SX.sym('U', nu, N)
    cost, constraints = 0, [X[:, 0] - x0]
    for k in range(N):
        cost += 0.5 * (ca.mtimes([X[:, k].T, Q, X[:, k]]) + ca.mtimes([U[:, k].T, R, U[:, k]]))
        constraints.append(F(X[:, k], U[:, k]) - X[:, k + 1])
    cost += 0.5 * ca.mtimes([X[:, N].T, Q, X[:, N]])
    nlp = {'x': ca.vertcat(ca.vec(X), ca.vec(U)), 'f': cost, 'g': ca.vertcat(*constraints)}
    solver = ca.nlpsol('solver', 'ipopt', nlp,
        {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.tol': 1e-12})
    w = np.array(solver(x0=0, lbg=0, ubg=0)['x']).flatten()
    return w[nx * (N + 1):]


def test_sqp_matches_ipopt(tmp_path):
    workdir = str(tmp_path / 'sqp_mpc')
    shutil.copytree(os.path.join(ROOT, 'examples', 'sqp_mpc'), workdir,
        ignore=shutil.ignore_patterns('__pmt_cache__'))
    code, output = run_pmt(workdir, 'sqp_mpc.py', cgen=True)
    assert code == 0, output
    u = np.array([float(line.split('=')[1]) for line in output.splitlines()
        if line.startswith('u = ')])
    assert len(u) == N, output
    # the solution is printed with 10 decimals
    assert np.abs(u - ipopt_solution()).max() < 1e-9
