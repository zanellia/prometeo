from prometeo import *

n: dims  = 2
m: dims  = 1


# class my_class():
#     def __init__(self) -> None:
#         A: pmat = pmat(1, n)
#         A[0,0] = 1.0
#         A[0,1] = 0.0
#         A[0,0] = 0.0
#         A[0,1] = 1.0

#         v: pvec = pvec(n)

#         v[0] = 1.0
#         v[0] = 0.0
#         v[1] = 0.0
#         v[1] = 1.0

#         x : ca = ca.SX.sym('x', 1, 1) 
#         test_fun : pfun = pfun('test_fun', 'ca.mtimes(A, v) + sin(x)', \
#             {'A': A, 'v': v, 'x': x})
        
#         self.test_fun : pfun = test_fun
#         # TODO(andrea): no way to call this from outside the 
#         # constructor as of now!

#         return


def main() -> int:

    A: pmat = pmat(m, n)
    A[0,0] = 1.0
    A[0,1] = 0.0
    A[0,0] = 0.0
    A[0,1] = 1.0

    v: pvec = pvec(n)
    v[0] = 1.0
    v[0] = 0.0
    v[1] = 0.0
    v[1] = 1.0

    # TODO(andrea): how about using something like this?
    # @casadi
    # def test_fun([[n,n]], [[m,n]], [A, v])
    #     x : ca = ca.SX.sym('x', 1, 1) 
    #     exp = ca.mtimes(A, v) + sin(x)
    #     test_fun : pfun2 = pfun2('test_fun', [x], [exp], [A, v])

    x : ca = ca.SX.sym('x', 2, 1) 
    test_fun : pfun = pfun('test_fun', 'ca.mtimes(A, v) + ca.sin(x[0,0]) + ca.dot(x,x)', \
        {'A': A, 'v': v, 'x': x})
    
    res : pmat = pmat(m, m)
    res[0,0] = 0.1
    res = test_fun(res)
    
    print(res)

    # test_jac : pfun = pfun('test_jac', 'ca.jacobian( \
    #     ca.mtimes(A, v) + sin(x), x)', \
    #     {'A': A, 'v': v, 'x': x})
    
    # res = test_jac(1.0)

    # # C : my_class = my_class()

    # def myfun(a : int) -> int: 
    #     print('YO')
    #     return 0

    # print(res)

    return 0


