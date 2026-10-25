"""The OCPs of examples/sqp_mpc solved with acados (SQP with HPIPM, no
condensing): solution and timings, for comparison with prometeo.

usage: python acados_sqp.py [cartpole | chain [n_free]] [repetitions]
"""
import sys
import numpy as np
import casadi as ca
from acados_template import AcadosOcp, AcadosOcpSolver, AcadosModel

N = 20
n_mpc = 30


def cartpole():
    # examples/sqp_mpc/sqp_mpc.py
    M, m, l, g = 1.0, 0.1, 0.8, 9.81
    nx, nu = 4, 1

    def f(x, u):
        s, c = ca.sin(x[1]), ca.cos(x[1])
        d = M + m - m * c * c
        return ca.vertcat(x[2], x[3], (-m * l * s * x[3] ** 2 + m * g * c * s + u[0]) / d,
            (-m * l * c * s * x[3] ** 2 + u[0] * c + (M + m) * g * s) / (l * d))

    return dict(name='cartpole', nx=nx, nu=nu, h=0.05, f=f,
        Q=np.diag([10.0, 10.0, 0.1, 0.1]), R=np.diag([0.1]),
        x0=np.array([0.0, 0.4, 0.0, 0.0]), u_max=5.0)


def chain(n_free):
    # examples/sqp_mpc/chain_mpc.py: dynamics in deviation from the rest position
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
    return dict(name='chain%d' % n_free, nx=nx, nu=nu, h=0.1, f=lambda x, u: f_abs(x + rest, u),
        Q=np.diag([1.0] * (3 * n_free + 3) + [0.1] * (3 * n_free)), R=0.01 * np.eye(nu),
        x0=x0, u_max=1.0)


def solver(problem, rti):
    nx, nu = problem['nx'], problem['nu']
    mdl = AcadosModel()
    mdl.name = problem['name']
    mdl.x, mdl.u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
    mdl.f_expl_expr = problem['f'](mdl.x, mdl.u)
    ocp = AcadosOcp()
    ocp.model = mdl
    ocp.solver_options.N_horizon = N
    ocp.solver_options.tf = N * problem['h']
    # LINEAR_LS cost 1/2 ||y||^2_W = 1/2 x'Qx + 1/2 u'Ru
    ocp.cost.cost_type = 'LINEAR_LS'
    ocp.cost.cost_type_e = 'LINEAR_LS'
    ocp.cost.W = np.block([[problem['Q'], np.zeros((nx, nu))], [np.zeros((nu, nx)), problem['R']]])
    ocp.cost.W_e = problem['Q']
    ocp.cost.Vx = np.vstack([np.eye(nx), np.zeros((nu, nx))])
    ocp.cost.Vu = np.vstack([np.zeros((nx, nu)), np.eye(nu)])
    ocp.cost.Vx_e = np.eye(nx)
    ocp.cost.yref = np.zeros(nx + nu)
    ocp.cost.yref_e = np.zeros(nx)
    ocp.constraints.lbu = -problem['u_max'] * np.ones(nu)
    ocp.constraints.ubu = problem['u_max'] * np.ones(nu)
    ocp.constraints.idxbu = np.arange(nu)
    ocp.constraints.x0 = problem['x0']
    opts = ocp.solver_options
    # by default acados scales the stage costs by the time step
    opts.cost_scaling = np.ones(N + 1)
    opts.integrator_type = 'ERK'
    opts.sim_method_num_stages = 4
    opts.sim_method_num_steps = 1
    opts.hessian_approx = 'GAUSS_NEWTON'
    opts.qp_solver = 'PARTIAL_CONDENSING_HPIPM'
    opts.qp_solver_cond_N = N
    opts.qp_solver_iter_max = 50
    opts.qp_solver_warm_start = 0
    for tol in ('qp_solver_tol_stat', 'qp_solver_tol_eq', 'qp_solver_tol_ineq', 'qp_solver_tol_comp'):
        setattr(opts, tol, 1e-12)
    opts.nlp_solver_type = 'SQP_RTI' if rti else 'SQP'
    opts.nlp_solver_max_iter = 50
    for tol in ('nlp_solver_tol_stat', 'nlp_solver_tol_eq', 'nlp_solver_tol_ineq', 'nlp_solver_tol_comp'):
        setattr(opts, tol, 1e-10)
    opts.globalization = 'FIXED_STEP'
    opts.print_level = 0
    name = problem['name'] + ('_rti' if rti else '_sqp')
    ocp.code_export_directory = 'c_generated_code_' + name
    return AcadosOcpSolver(ocp, json_file='acados_ocp_{}.json'.format(name), verbose=False)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'chain':
        n_free = int(args[1]) if len(args) > 1 else 3
        problem = chain(n_free)
        args = args[2:]
    else:
        problem = cartpole()
        args = args[1:] if args and args[0] == 'cartpole' else args
    reps = int(args[0]) if args else 200
    nx, nu, h, x0 = problem['nx'], problem['nu'], problem['h'], problem['x0']
    sqp = solver(problem, rti=False)
    rti = solver(problem, rti=True)
    x, u = ca.SX.sym('x', nx), ca.SX.sym('u', nu)
    f = problem['f']
    k1 = f(x, u); k2 = f(x + h / 2 * k1, u); k3 = f(x + h / 2 * k2, u); k4 = f(x + h * k3, u)
    F = ca.Function('F', [x, u], [x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)])

    # full SQP solve from zero, repeated for timing
    times = []
    for r in range(reps):
        sqp.reset()
        sqp.solve_for_x0(x0, fail_on_nonzero_status=False)
        times.append(sqp.get_stats('time_tot'))
    u_sol = np.array([sqp.get(k, 'u') for k in range(N)])
    print('sqp status', sqp.get_status(), 'iterations', sqp.get_stats('sqp_iter'),
        'qp iterations', int(sum(sqp.get_stats('qp_iter'))))
    np.savetxt('u_acados_%s.txt' % problem['name'], u_sol.flatten())
    print('SQP solve: min %.1f us, median %.1f us' % (1e6 * min(times), 1e6 * np.median(times)))

    # closed loop: one RTI per step, warm started from the solution
    for k in range(N):
        rti.set(k, 'u', sqp.get(k, 'u'))
        rti.set(k, 'x', sqp.get(k, 'x'))
    rti.set(N, 'x', sqp.get(N, 'x'))
    xp = x0.copy()
    rti_times = []
    rti_qp_iters = []
    for t in range(n_mpc):
        rti.solve_for_x0(xp, fail_on_nonzero_status=False)
        rti_times.append(rti.get_stats('time_tot'))
        rti_qp_iters.append(int(np.sum(rti.get_stats('qp_iter'))))
        xp = np.array(F(xp, rti.get(0, 'u'))).flatten()
    print('RTI step: min %.1f us, median %.1f us, total %.1f us for %d steps, qp iterations per step %.1f' % (
        1e6 * min(rti_times), 1e6 * np.median(rti_times), 1e6 * sum(rti_times), n_mpc, np.mean(rti_qp_iters)))
    print('closed-loop state', np.round(xp, 5))
