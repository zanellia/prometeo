from prometeo.linalg import *
import sys 

n: int = 10

A: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        A[i][j] = i*n + j 

B: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        B[i][j] = 0.0 

for i in range(n):
    B[i][i] = 1.0 

C: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        C[i][j] = 0.0 

i: int = 0.0
while i < n:
    i = i + 1

if i >= 5:
    i = i *2

prmt_gemm_nt(A, B, C, C)

# print results
print('\n\nB = ')
prmt_print(B)
print('\n\nA = ')
prmt_print(A)
print('\n\nC = ')
prmt_print(C)

