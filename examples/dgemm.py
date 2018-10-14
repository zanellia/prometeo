# from prometeo.linalg import *

# class p_class:
#     attr_1: int = 1
#     attr_2: double = 3.0

#     def method_1(arg1: prmt_mat, arg2: prmt_mat) -> double:
#         a: double = arg1.field1
#         b: double = arg2.field2
#         copyarg2: double = arg2
#         c: double = a*b + b*a*a
#         return c

def function1(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
    C = A * B
    prmt_print(C)
    return


def main() -> None:

    # test_class: p_class
    n_list: List[int]

    pmat_list: List[prmt_mat]

    n: int = 10

    A: prmt_mat = prmt_mat(n, n)
    prmt_fill(A, 1.0)

    B: prmt_mat = prmt_mat(n, n)
    prmt_fill(B, 2.0)

    C: prmt_mat = prmt_mat(n, n)

    prmt_print(C)
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

if __name__ == "__main__":
    # execute only if run as a script
    main()
