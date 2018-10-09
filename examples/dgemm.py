# from prometeo.linalg import *
# import sys 

n: int = 10

A: prmt_mat = prmt_mat(n, n)
A.fill(1.0)

B: prmt_mat = prmt_mat(n, n)
B.fill(2.0)

C: prmt_mat = prmt_mat(n, n)

prmt_print(C)
C = A * B
prmt_print(C)
C = A + B
prmt_print(C)
C = A - B
prmt_print(C)

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
prmt_print(C)

# C = (A + B*prmt_ls(A, B, 'lu'))*(B + C)

