"""Check the SQP examples (examples/sqp_mpc) against an independent solution
of the same optimal control problems computed with CasADi and IPOPT."""

import os
import shutil

import casadi as ca
import numpy as np
import pytest

from pmt_testing import run_pmt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 20


def cartpole():
    # as in examples/sqp_mpc/sqp_mpc.py
    M, m, l, g = 1.0, 0.1, 0.8, 9.81

    def f(x, u):
        s, c = ca.sin(x[1]), ca.cos(x[1])
        d = M + m - m * c * c
        return ca.vertcat(x[2], x[3],
            (-m * l * s * x[3] ** 2 + m * g * c * s + u[0]) / d,
            (-m * l * c * s * x[3] ** 2 + u[0] * c + (M + m) * g * s) / (l * d))

    return dict(nx=4, nu=1, h=0.05, f=f, Q=np.diag([10.0, 10.0, 0.1, 0.1]),
        R=np.diag([0.1]), x0=np.array([0.0, 0.4, 0.0, 0.0]), u_max=5.0)


def chain(n_free=3):
    # as in examples/sqp_mpc/chain_mpc.py: deviation from the rest position
    m, D, L0, g, p_end = 0.033, 1.0, 0.033, 9.81, 1.0
    nx, nu = 6 * n_free + 3, 3

    def f_abs(x, u):
        p = [ca.DM.zeros(3)] + [x[3 * i:3 * i + 3] for i in range(n_free + 1)]
        forces = []
        for j in range(n_free + 1):
            d = p[j + 1] - p[j]
            forces.append(D * (1 - L0 / ca.norm_2(d)) * d)
        acc = [(forces[i + 1] - forces[i]) / m - ca.vertcat(0, 0, g) for i in range(n_free)]
        return ca.vertcat(x[3 * n_free + 3:], u, *acc)

    end = ca.DM([p_end, 0, 0])
    z = ca.SX.sym('z', 3 * n_free)
    xz = ca.vertcat(z, end, ca.DM.zeros(3 * n_free))
    residual = ca.Function('residual', [z], [f_abs(xz, ca.DM.zeros(nu))[3 * n_free + 3:]])
    guess = ca.vertcat(*[end * (i + 1) / (n_free + 1) for i in range(n_free)])
    rest = ca.vertcat(ca.rootfinder('rest', 'newton', residual)(guess), end, ca.DM.zeros(3 * n_free))
    x0 = np.zeros(nx)
    x0[3 * n_free + 4::3] = 1.0
    return dict(nx=nx, nu=nu, h=0.1, f=lambda x, u: f_abs(x + rest, u),
        Q=np.diag([1.0] * (3 * n_free + 3) + [0.1] * (3 * n_free)), R=0.01 * np.eye(nu),
        x0=x0, u_max=1.0)


def ipopt_solution(problem):
    nx, nu, h, f = problem['nx'], problem['nu'], problem['h'], problem['f']
    Q, R, x0, u_max = problem['Q'], problem['R'], problem['x0'], problem['u_max']
    x, u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
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
    # no relaxation of the bounds, to compare with the exact solution
    solver = ca.nlpsol('solver', 'ipopt', nlp, {'ipopt.print_level': 0, 'print_time': 0,
        'ipopt.tol': 1e-12, 'ipopt.bound_relax_factor': 0.0})
    lbx = [-np.inf] * (nx * (N + 1)) + [-u_max] * (nu * N)
    ubx = [np.inf] * (nx * (N + 1)) + [u_max] * (nu * N)
    w = np.array(solver(x0=0, lbg=0, ubg=0, lbx=lbx, ubx=ubx)['x']).flatten()
    # inputs, stage by stage
    return w[nx * (N + 1):]


@pytest.mark.parametrize('program, problem', [('sqp_mpc', cartpole), ('sqp_mpc_hl', cartpole),
    ('chain_mpc', chain)])
def test_sqp_matches_ipopt(tmp_path, program, problem):
    problem = problem()
    workdir = str(tmp_path / 'sqp_mpc')
    shutil.copytree(os.path.join(ROOT, 'examples', 'sqp_mpc'), workdir,
        ignore=shutil.ignore_patterns('__pmt_cache__'))
    code, output = run_pmt(workdir, program + '.py', cgen=True)
    assert code == 0, output
    u = np.array([float(line.split('=')[1]) for line in output.splitlines()
        if line.startswith('u = ')])
    assert len(u) == N * problem['nu'], output
    u_ipopt = ipopt_solution(problem)
    # some bounds are active at the solution
    assert np.isclose(np.abs(u_ipopt).max(), problem['u_max'])
    # the solution is printed with 10 decimals
    assert np.abs(u - u_ipopt).max() < 1e-9
