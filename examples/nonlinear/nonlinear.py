from prometeo import *
from prometeo.nonlinear import pfun
import casadi as ca

n: dims  = 2

def main() -> int:

    A: pmat = pmat(1, n)
    A[0,0] = 1.0
    A[0,1] = 0.0
    A[0,0] = 0.0
    A[0,1] = 1.0

    v: pvec = pvec(n)
    v[0] = 1.0
    v[0] = 0.0
    v[1] = 0.0
    v[1] = 1.0

    x : ca = ca.SX.sym('x', 1, 1) 
    fun = pfun('test_fun', 'A*v + sin(x)', {'A': A, 'v': v, 'x': x})
    import pdb; pdb.set_trace()
    return 0


