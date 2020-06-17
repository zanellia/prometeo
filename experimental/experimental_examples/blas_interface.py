from prometeo import *

n: dims = 10

A: pmat = pmat(n, n)
for i in range(n):
    for j in range(n):
        A[i,j] = i*n + j 

B: pmat = pmat(n, n)
for i in range(n):
    for j in range(n):
        B[i,j] = 0.0 

for i in range(n):
    B[i,i] = 1.0 

C: pmat = pmat(n, n)
for i in range(n):
    for j in range(n):
        C[i,j] = 0.0 

pmt_gemm_nt(A.T, B, C, C)
# pmt_gemm_nt(A, B.T, C, C)
pmt

# print results
print('\n\nB = ')
pmt_print(B)
print('\n\nA = ')
pmt_print(A)
print('\n\nC = ')
pmt_print(C)

