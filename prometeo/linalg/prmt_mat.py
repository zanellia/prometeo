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
    
    def fill(self, value):
        for i in range(self.blasfeo_dmat.m):
            for j in range(self.blasfeo_dmat.n):
                self[i][j] = value
        return

    def copy(self, to_be_copied):
        for i in range(self.blasfeo_dmat.m):
            for j in range(self.blasfeo_dmat.n):
                value = to_be_copied[i][j]
                self[i][j] = value
        return
    
    # TODO(andrea): ideally one would have three levels:
    # 1) high-level
    # 2) intermediate-level 
    # 3) low-level (BLASFEO wrapper)

    # high-level linear algebra
    def __mul__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        res.fill(0.0)
        zero_mat = prmt_mat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        zero_mat.fill(0.0)
        prmt_gemm_nn(self, other, zero_mat, res)
        return res

    def __add__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        res.fill(0.0)
        res.copy(other)
        prmt_gead(1.0, self, res)
        return res 

    def __sub__(self, other):
        res = prmt_mat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        res.fill(0.0)
        res.copy(other)
        prmt_gead(-1.0, self, res)
        return res 

def prmt_ls(A: prmt_mat, B: prmt_mat, opts: string):
    res  = prmt_mat(A.blasfeo_dmat.m, B.blasfeo_dmat.n)
    fact = prmt_mat(A.blasfeo_dmat.m, B.blasfeo_dmat.m)
    if opts is 'ch':
        raise NotImplementedError
    elif opts is 'lu':
        # create prmt_mat for factor
        fact = prmt_mat(A.blasfeo_dmat.m, A.blasfeo_dmat.n)
        fact.copy(A)
        # create permutation vector
        ipivm = cast(A.blasfeo_dmat.m, POINTER(c_int))
        # factorize
        prmt_getrf(fact, ipiv)
        # create permuted rhs
        pB = prmt_mat(B.blasfeo_dmat.m, B.blasfeo_dmat.n)
        pB.copy(B)
        c_prmt_rowpe(B.blasfeo_dmat.m, ipiv, pB)
        # solve
        prmt_trsm_llnu(nx * ns, nx + nu, 1.0, JGK, 0, 0, &JKf[ss], 0, 0, &JKf[ss], 0, 0);
        prmt_trsm_lunn(nx * ns, nx + nu, 1.0, JGK, 0, 0, &JKf[ss], 0, 0, &JKf[ss], 0, 0);

    elif opts is 'qr':
        raise NotImplementedError
    elif opts is 'lq':
        raise NotImplementedError
    else:
        return 

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

def prmt_trsm_llnu(m: int, n: int, alpha: float, A: prmt_mat, B: prmt_mat):
    c_prmt_trsm_llnu(m, n, alpha, A, B);
    return 

def prmt_trsm_lunn(m: int, n: int, alpha: float, A: prmt_mat, B: prmt_mat):
    c_prmt_trsm_lunn(m, n, alpha, A, B);
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


