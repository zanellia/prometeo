from prmt_mat import *
from blasfeo_wrapper import *

n: int = 10

void_p = int 

data_A: void_p = (POINTER(c_double) * 1)()
bw.d_zeros(byref(data_A), n, n)
for i in range(n*n):
    data_A[0][i] = i
A: prmt_mat = prmt_mat(n, n, data_A)

data_B: void_p = (POINTER(c_double) * 1)()
bw.d_zeros(byref(data_B), n, n)
for i in range(n):
    data_B[0][i*(n + 1)] = 1.0
B: prmt_mat = prmt_mat(n, n, data_B)

data_C: void_p = (POINTER(c_double) * 1)()
bw.d_zeros(byref(data_C), n, n)
C: prmt_mat = prmt_mat(n, n, data_C)

dgemm_nt(A, B, C, C)

# print results
print('\n\nB = ')
B.print()
print('\n\nA = ')
A.print()
print('\n\nC = ')
C.print()

