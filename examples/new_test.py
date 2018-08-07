# from prometeo.linalg import *
# import sys 

n: int = 10

A: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        prmt_set(A, i*n + j, i, j) 

B: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        prmt_set(B, 0.0, i, j) 

for i in range(n):
    prmt_set(B, 1.0, i, i) 

C: prmt_mat = prmt_mat(n, n)
for i in range(n):
    for j in range(n):
        prmt_set(C, 0.0, i, j) 

i: int = 0.0
while i < n:
    i = i + 1

if i >= 5:
    i = i *2

prmt_dgemm_nt(A, B, C, C)

# print results
print('\n\nB = ')
prmt_print(B)
print('\n\nA = ')
prmt_print(A)
print('\n\nC = ')
prmt_print(C)

