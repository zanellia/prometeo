# from prometeo.linalg import *

class p_class:
    attr_1: int = 1
    # attr_2: double = 3.0
    attr_2: float = 3.0

    # def method_1(arg1: prmt_mat, arg2: prmt_mat) -> double:
    #     a: double = arg1.field1
    #     b: double = arg2.field2
    #     copyarg2: double = arg2
    #     c: double = a*b + b*a*a
    #     return c

    def method_2(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> void:
    # def method_2(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
        C = A * B
        prmt_print(C)
        return

def function1(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
    C = A * B
    prmt_print(C)
    return


def main() -> None:

    test_class: p_class
    test_class.attr_1 = 2


    j: int = 0
    for i in range(10):
        j = j + 1

    while j > 0:
        j = j - 1


    # n_list: List[int] = [int] * 10 
    # n_list[0] = 1

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

    # pmat_list: List[prmt_mat]
    # pmat_list[0] = A

    # prmt_print(C)
    C = A * B
    prmt_print(C)
    C = A + B
    prmt_print(C)
    C = A - B
    prmt_print(C)
    function1(A, B, C)
    # C = A|B
    # C = A * B + C
    # C = C + A * B
    # C = A\B
    # C = A\(B, 'lu')

    # C = A + prmt_ls(A, B, 'lu')

    # C = A + B + C

    # C = A + prmt_ls(A, B, 'lu')
    # prmt_print(C)

    # C = prmt_ls(A, B, 'lu')
    # prmt_print(C)

    # C = (A + B*prmt_ls(A, B, 'lu'))*(B + C)

# if __name__ == "__main__":
#     # execute only if run as a script
#     main()
