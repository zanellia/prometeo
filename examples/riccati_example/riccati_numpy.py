from numpy import *
from scipy import linalg

nx = 2
nu = 2
nxu = 4
N = 5

A = array([[0.8, 0.1], [0.3, 0.8]])
B = array([[1.0, 0.0], [0.0, 1.0]])
Q = array([[1.0, 0.0], [0.0, 1.0]])
R = array([[1.0, 0.0], [0.0, 1.0]])
P = Q

BA = zeros((nx, nxu))
M = zeros((nxu, nxu))
Mxx = zeros((nx, nx))
for i in range(N):
    BA = concatenate((B,A),1)
    BAtP = dot(transpose(BA), P)
    M = zeros((nxu, nxu))
    M[0:nu, 0:nu] = R
    M[nu:nu+nx, nu:nu+nx] = Q
    M = M + dot(BAtP, BA)
    L = linalg.cholesky(M)
    print('L:\n', L)
    Mxx = L[nu:nu+nx, nu:nu+nx]
    P = dot(transpose(Mxx), Mxx)
    print('P:\n', P)

P = Q
for i in range(N):
    P = Q + dot(transpose(A),dot(P,A)) - dot(dot(transpose(A),dot(P,B)), \
        linalg.solve(R + dot(transpose(B), dot(P,B)), \
        dot(dot(transpose(B),P), A)))

    print('P:\n', P)

