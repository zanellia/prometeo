from ctypes import *
from .prmt_mat_blasfeo_wrapper import *
from .prmt_vec_blasfeo_wrapper import *
from .blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat = None
    _i = None
    _j = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_blasfeo_dmat(m, n)  
    
    def __getitem__(self, index):
        if self._i is not None:
            self._j = index
            el = self.my_get_item()
            return el

        self._i = index
        return self

    def __setitem__(self, index, value):
        self._j = index
        self.my_set_item(value)
        return
   

    def my_set_item(self, value):
        prmt_set(self, value, self._i, self._j)
        self._i = None
        self._j = None
        return

    def my_get_item(self):
        el = prmt_get(self, self._i, self._j)
        self._i = None
        self._j = None
        return el 
    
    
    # TODO(andrea): ideally one would have three levels:
    # 1) high-level
    # 2) intermediate-level 
    # 3) low-level (BLASFEO wrapper)

    # high-level linear algebra
    def __mul__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        prmt_fill(res, 0.0)
        zero_mat = prmt_mat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        prmt_fill(zero_mat, 0.0)
        prmt_gemm_nn(self, other, zero_mat, res)
        return res

    def __add__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        prmt_copy(other, res)
        prmt_gead(1.0, self, res)
        return res 

    def __sub__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        prmt_copy(self, res)
        prmt_gead(-1.0, other, res)
        return res 

def prmt_fill(A: prmt_mat, value):
    for i in range(A.blasfeo_dmat.m):
        for j in range(A.blasfeo_dmat.n):
            A[i][j] = value
    return

def prmt_copy(A: prmt_mat, B: prmt_mat):
    for i in range(A.blasfeo_dmat.m):
        for j in range(A.blasfeo_dmat.n):
            B[i][j] = A[i][j]
    return

def prmt_lus(A: prmt_mat, B: prmt_mat, opts):
    res  = prmt_mat(A.blasfeo_dmat.m, B.blasfeo_dmat.n)
    fact = prmt_mat(A.blasfeo_dmat.m, B.blasfeo_dmat.m)
    # create prmt_mat for factor
    fact = prmt_mat(A.blasfeo_dmat.m, A.blasfeo_dmat.n)
    prmt_copy(A, fact)
    # create permutation vector
    ipiv = cast(create_string_buffer(A.blasfeo_dmat.m*A.blasfeo_dmat.m), POINTER(c_int))
    # factorize
    prmt_getrf(fact, ipiv)
    # create permuted rhs
    pB = prmt_mat(B.blasfeo_dmat.m, B.blasfeo_dmat.n)
    prmt_copy(B, pB)
    prmt_rowpe(B.blasfeo_dmat.m, ipiv, pB)
    # solve
    prmt_trsm_llnu(A, pB)
    prmt_trsm_lunn(A, pB)
    return pB

# intermediate-level linear algebra
def prmt_gemm_nn(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nn(A, B, C, D)
    return

def prmt_gemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nt(A, B, C, D)
    return

def prmt_gemm_tn(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_tn(A, B, C, D)
    return

def prmt_gemm_tt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_tt(A, B, C, D)
    return

def prmt_gead(alpha: float, A: prmt_mat, B: prmt_mat):
    c_prmt_dgead(alpha, A, B)
    return

def prmt_rowpe(m: int, ipiv: POINTER(c_int), A: prmt_mat):
    c_prmt_drowpe(m, ipiv, A)
    return

def prmt_trsm_llnu(A: prmt_mat, B: prmt_mat):
    c_prmt_trsm_llnu(A, B)
    return 

def prmt_trsm_lunn(A: prmt_mat, B: prmt_mat):
    c_prmt_trsm_lunn(A, B)
    return

def prmt_getrf(fact: prmt_mat, ipiv):
    c_prmt_getrf(fact, ipiv);
    return 

# auxiliary functions
def prmt_set_data(M: prmt_mat, data: POINTER(c_double)):
    c_prmt_set_blasfeo_dmat(M.blasfeo_dmat, data)  
    return

def prmt_set(M: prmt_mat, value, i, j):
    c_prmt_set_blasfeo_dmat_el(value, M.blasfeo_dmat, i, j)  
    return

def prmt_get(M: prmt_mat, i, j):
    el = c_prmt_get_blasfeo_dmat_el(M.blasfeo_dmat, i, j)  
    return el 

def prmt_print(M: prmt_mat):
    c_prmt_print_blasfeo_dmat(M)
    return  


