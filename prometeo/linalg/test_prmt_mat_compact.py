from prmt_mat import *
from blasfeo_wrapper import *

n: int = 10

void_p = int 

A: prmt_mat = prmt_mat(n, n)
for i in range(n*n):
    A[0][i] = i

B: prmt_mat = prmt_mat(n, n)
for i in range(n):
    B[0][i*(n + 1)] = 1.0

C: prmt_mat = prmt_mat(n, n)

dgemm_nt(A, B, C, C)

# print results
print('\n\nB = ')
B.print()
print('\n\nA = ')
A.print()
print('\n\nC = ')
C.print()

