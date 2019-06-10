# UNCOMMENT THESE LINES TO EXECUTE 
# from prometeo.linalg import *
# from prometeo.auxl import *

class p_class:
    attr_1: int = 1
    attr_2: float = 3.0

    def method_2(self, A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
        C = A * B
        prmt_print(C)
        return

def function1(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
    C = A * B
    prmt_print(C)
    return

def main() -> None:

    n_list: List[int] = prmt_list(int, 10) 
    n_list[0] = 1

    test_class: p_class = p_class()
    test_class.attr_1 = 2

    j: int = 0
    for i in range(10):
        j = j + 1

    while j > 0:
        j = j - 1

    n: int = 10
    A: prmt_mat = prmt_mat(n, n)
    A[0][2] = 2.0

    for i in range(2):
        A[0][i] = A[0][i]

    prmt_fill(A, 1.0)

    B: prmt_mat = prmt_mat(n, n)
    prmt_fill(B, 2.0)

    C: prmt_mat = prmt_mat(n, n)

    test_class.method_2(A, B, C)

    pmat_list: List[prmt_mat] = prmt_list(prmt_mat, 10)
    pmat_list[0] = A

    C = A * B
    prmt_print(C)
    C = A + B
    prmt_print(C)
    C = A - B
    prmt_print(C)
    function1(A, B, C)
    function1(pmat_list[0], B, C)

    prmt_fill(A, 0.0)
    for i in range(10):
        A[i][i] = 1.0

    prmt_print(A)

    # still to be implemented in code-generator
    a : prmt_vec = prmt_vec(10)
    # a.fill(0.0)
    a[1] = 2.0
    el = a[1]
    prmt_vec_print(a)

    c : prmt_vec = prmt_vec(10)
    c = A*a
    prmt_vec_print(c)

    # prmt_lus(A, B, C)
    # prmt_print(C)
    # D: prmt_mat = prmt_mat(n, n)
    # D = A*C
    # prmt_print(D)

# UNCOMMENT THESE LINES TO EXECUTE 
# if __name__ == "__main__":
    # execute only if run as a script
    # main()
