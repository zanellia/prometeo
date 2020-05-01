from prometeo import *

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
    test_fun : pfun = pfun('test_fun', 'ca.mtimes(A, v) + sin(x)', \
        {'A': A, 'v': v, 'x': x})
    
    res : float = 0.0
    res = test_fun(1.0)
    
    # print(res)

    test_jac : pfun = pfun('test_jac', 'ca.jacobian( \
        ca.mtimes(A, v) + sin(x), x)', \
        {'A': A, 'v': v, 'x': x})
    
    res = test_jac(1.0)

    # print(res)

    return 0


