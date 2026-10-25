"""CasADi functions callable from prometeo code.

A CasADi function is created in a pure Python block and wrapped:

    # pure >
    import casadi as ca
    x = ca.SX.sym('x', nx)
    ...
    f = casadi_function(ca.Function('f', [x, u], [y, ca.jacobian(y, x)]))
    # pure <

and called from prometeo code with matrices, inputs first and then the
outputs, which are written in place:

    f(x, u, y, J)

In Python, the wrapper evaluates the function numerically. When transpiling,
prometeo generates C code for it with CasADi's code generator and a wrapper
that copies matrices to and from static buffers (see casadi_codegen.py).
"""

import casadi as ca
import numpy as np


class casadi_function:

    def __init__(self, function):
        if not isinstance(function, ca.Function):
            raise TypeError('casadi_function expects a casadi.Function, not {}'.format(
                type(function).__name__))
        for i in range(function.n_in()):
            if not function.sparsity_in(i).is_dense():
                raise ValueError('input {} of CasADi function {} must be dense'.format(
                    i, function.name()))
        self.name = function.name()
        self.n_in = function.n_in()
        self.n_out = function.n_out()
        self.in_shapes = [(function.size1_in(i), function.size2_in(i)) for i in range(self.n_in)]
        self.out_shapes = [(function.size1_out(i), function.size2_out(i)) for i in range(self.n_out)]
        # dense outputs (e.g. Jacobians are sparse), as stored in a pmat
        inputs = function.mx_in()
        outputs = function.call(inputs)
        self.function = ca.Function(self.name, inputs, [ca.densify(o) for o in outputs])

    def renamed(self, name):
        """The (dense) CasADi function under another name."""
        inputs = self.function.mx_in()
        return ca.Function(name, inputs, self.function.call(inputs))

    def __call__(self, *args):
        if len(args) != self.n_in + self.n_out:
            raise TypeError('CasADi function {} takes {} inputs and {} outputs, {} arguments '
                'given'.format(self.name, self.n_in, self.n_out, len(args)))
        shapes = self.in_shapes + self.out_shapes
        for k, (A, (m, n)) in enumerate(zip(args, shapes)):
            if (A.m, A.n) != (m, n):
                kind = 'input {}'.format(k) if k < self.n_in else 'output {}'.format(k - self.n_in)
                raise ValueError('CasADi function {}: {} has size {}x{}, expected {}x{}'.format(
                    self.name, kind, A.m, A.n, m, n))
        inputs = [np.array([[A[i, j] for j in range(A.n)] for i in range(A.m)])
            for A in args[:self.n_in]]
        results = self.function.call(inputs)
        for A, value in zip(args[self.n_in:], results):
            value = np.array(value)
            for i in range(A.m):
                for j in range(A.n):
                    A[i, j] = float(value[i, j])
