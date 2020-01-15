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
Mu = zeros((nu, nu))
Mxu = zeros((nx, nu))
Mux = zeros((nu, nxu))
Mxx = zeros((nx, nx))
for i in range(N):
    BA = concatenate((B,A),1)
    BAtP = dot(transpose(BA), P)
    M = zeros((nxu, nxu))
    M[0:nu, 0:nu] = R
    M[nu:nu+nx, nu:nu+nx] = Q
    M = M + dot(BAtP, BA)
    Mu[:nu, 0:nu] = M[0:nu, 0:nu]
    Lu = linalg.cholesky(Mu)
    Mux = M[0:nu, nx:nu+nx]
    Mux = linalg.blas.dtrsm(1.0, transpose(Lu), Mux, lower=1)
    Mux = linalg.blas.dtrsm(1.0, Lu, Mux, lower=0)
    Mxu[0:nx, 0:nu] = M[nu:nu+nx, 0:nu]
    Mxx[0:nx, 0:nx] = M[nu:nu+nx, nu:nu+nx]
    P = Q + Mxx - dot(Mxu, Mux)
    print('P:\n', P)

