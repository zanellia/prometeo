from ctypes import *
from .pmat_blasfeo_wrapper import *
from .pvec import *
from .blasfeo_wrapper import *
from multipledispatch import dispatch
from abc import ABC

class pmat_(ABC):
    pass

class pmat(pmat_):
    blasfeo_dmat = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_pmt_create_blasfeo_dmat(m, n)  

    def __getitem__(self, index):
        if isinstance(index, tuple):
            if len(index) == 2:
                el = pmat_get(self, index[0], index[1])
                return el
        else:
            raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                    you have: {}\n. Exiting'.format(index))

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            if len(index) == 2:
                pmat_set(self, value, index[0], index[1]) 
        else:
            raise Exception ('pmat subscripts must be 2-dimensional tuples, \
                    you have: {}\n. Exiting'.format(index))

# class pmat(pmat_):

#     blasfeo_dmat = None
#     _i = None
#     _j = None

#     def __init__(self, m: int, n: int):
#         self.blasfeo_dmat = c_pmt_create_blasfeo_dmat(m, n)  
    
#     def __getitem__(self, index):
#         if self._i is not None:
#             self._j = index
#             el = self.my_get_item()
#             return el

#         self._i = index
#         return self

#     def __setitem__(self, index, value):
#         self._j = index
#         self.my_set_item(value)
#         return
   

#     def my_set_item(self, value):
#         pmat_set(self, value, self._i, self._j)
#         self._i = None
#         self._j = None
#         return

#     def my_get_item(self):
#         el = pmat_get(self, self._i, self._j)
#         self._i = None
#         self._j = None
#         return el 
    
    
    # TODO(andrea): ideally one would have three levels:
    # 1) high-level
    # 2) intermediate-level 
    # 3) low-level (BLASFEO wrapper)

    # high-level linear algebra
    @dispatch(pmat_)
    def __mul__(self, other):
        if self.blasfeo_dmat.n != other.blasfeo_dmat.m:
            raise Exception('__mul__: mismatching dimensions:' 
                ' ({}, {}) x ({}, {})'.format(self.blasfeo_dmat.m, \
                self.blasfeo_dmat.n, other.blasfeo_dmat.m, \
                other.blasfeo_dmat.n))

        res = pmat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        pmat_fill(res, 0.0)
        zero_mat = pmat(self.blasfeo_dmat.m, other.blasfeo_dmat.n)
        pmat_fill(zero_mat, 0.0)
        pmt_gemm_nn(self, other, zero_mat, res)
        return res

    @dispatch(pvec_)
    def __mul__(self, other):
        if self.blasfeo_dmat.n != other.blasfeo_dvec.m:
            raise Exception('__mul__: mismatching dimensions:' 
                ' ({}, {}) x ({},)'.format(self.blasfeo_dmat.m, \
                self.blasfeo_dmat.n, other.blasfeo_dvec.m))

        res = pvec(self.blasfeo_dmat.m)
        res.fill(0.0)
        zero_vec = pvec(self.blasfeo_dmat.m)
        zero_vec.fill(0.0)
        pmt_gemv_n(self, other, zero_vec, res)
        return res

    @dispatch(pmat_)
    def __add__(self, other):
        if self.blasfeo_dmat.m != other.blasfeo_dmat.m \
                or self.blasfeo_dmat.n != other.blasfeo_dmat.n:
            raise Exception('__add__: mismatching dimensions:' 
                ' ({}, {}) + ({}, {})'.format(self.blasfeo_dmat.m, \
                self.blasfeo_dmat.n, other.blasfeo_dmat.m, \
                other.blasfeo_dmat.n))
        res = pmat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        pmat_copy(other, res)
        pmt_gead(1.0, self, res)
        return res 

    def __sub__(self, other):
        if self.blasfeo_dmat.m != other.blasfeo_dmat.m \
                or self.blasfeo_dmat.n != other.blasfeo_dmat.n:
            raise Exception('__sub__: mismatching dimensions:' 
                ' ({}, {}) + ({}, {})'.format(self.blasfeo_dmat.m, \
                self.blasfeo_dmat.n, other.blasfeo_dmat.m, \
                other.blasfeo_dmat.n))
        res = pmat(self.blasfeo_dmat.m, self.blasfeo_dmat.n)
        pmat_copy(self, res)
        pmt_gead(-1.0, other, res)
        return res 

def pmat_fill(A: pmat, value):
    for i in range(A.blasfeo_dmat.m):
        for j in range(A.blasfeo_dmat.n):
            A[i,j] = value
    return

def pmat_copy(A: pmat, B: pmat):
    for i in range(A.blasfeo_dmat.m):
        for j in range(A.blasfeo_dmat.n):
            B[i,j] = A[i,j]
    return

def pmt_getrsm(A: pmat, B: pmat, fact: pmat, ipiv: list, res: pmat):
    # create permutation vector
    c_ipiv = cast(create_string_buffer(sizeof(c_int)*A.blasfeo_dmat.m), POINTER(c_int))
    for i in range(A.blasfeo_dmat.n):
        c_ipiv[i] = ipiv[i]
    res  = pmat(A.blasfeo_dmat.m, B.blasfeo_dmat.n)
    # create permuted rhs
    # pB = pmat(B.blasfeo_dmat.m, B.blasfeo_dmat.n)
    pmat_copy(B, res)
    pmt_rowpe(B.blasfeo_dmat.m, c_ipiv, res)
    # solve
    pmt_trsm_llnu(A, res)
    pmt_trsm_lunn(A, res)
    return res

def pmt_getrsv(b: pvec, fact: pmat, ipiv: list, res: pvec):
    # create permutation vector
    c_ipiv = cast(create_string_buffer(sizeof(c_int)*fact.blasfeo_dmat.m), POINTER(c_int))
    for i in range(fact.blasfeo_dmat.n):
        c_ipiv[i] = ipiv[i]
    # permuted rhs
    pvec_copy(b, res)
    pmt_vecpe(b.blasfeo_dvec.m, c_ipiv, res)
    # solve
    pmt_trsv_llnu(fact, res)
    pmt_trsv_lunn(fact, res)
    return res

def pmt_potrsm(b: pmat, fact: pmat, res: pmat):
    # solve
    pmt_trsm_llnu(fact, res)
    pmt_trsm_lunn(fact, res)
    return res

def pmt_potrsv(b: pvec, fact: pmat, res: pvec):
    # solve
    pmt_trsv_llnu(fact, res)
    pmt_trsv_lunn(fact, res)
    return res

# intermediate-level linear algebra
def pmt_gemm_nn(A: pmat, B: pmat, C: pmat, D: pmat):
    c_pmt_dgemm_nn(A, B, C, D)
    return

def pmt_gemm_nt(A: pmat, B: pmat, C: pmat, D: pmat):
    c_pmt_dgemm_nt(A, B, C, D)
    return

def pmt_gemm_tn(A: pmat, B: pmat, C: pmat, D: pmat):
    c_pmt_dgemm_tn(A, B, C, D)
    return

def pmt_gemm_tt(A: pmat, B: pmat, C: pmat, D: pmat):
    c_pmt_dgemm_tt(A, B, C, D)
    return

def pmt_gead(alpha: float, A: pmat, B: pmat):
    c_pmt_dgead(alpha, A, B)
    return

def pmt_rowpe(m: int, ipiv: POINTER(c_int), A: pmat):
    c_pmt_drowpe(m, ipiv, A)
    return

def pmt_trsm_llnu(A: pmat, B: pmat):
    c_pmt_trsm_llnu(A, B)
    return 

def pmt_trsm_lunn(A: pmat, B: pmat):
    c_pmt_trsm_lunn(A, B)
    return

def pmt_trsv_llnu(A: pmat, b: pvec):
    c_pmt_trsv_llnu(A, b)
    return 

def pmt_trsv_lunn(A: pmat, b: pvec):
    c_pmt_trsv_lunn(A, b)
    return

def pmt_getrf(A: pmat, fact: pmat, ipiv: list):
    pmat_copy(A, fact)
    # create permutation vector
    c_ipiv = cast(create_string_buffer(sizeof(c_int)*A.blasfeo_dmat.m), POINTER(c_int))
    # factorize
    c_pmt_getrf(fact, c_ipiv)
    for i in range(A.blasfeo_dmat.n):
        ipiv[i] = c_ipiv[i]
    return 

def pmt_potrf(A: pmat, fact: pmat):
    pmat_copy(A, fact)
    # factorize
    c_pmt_potrf(fact)
    return 

def pmt_gemv_n(A: pmat, b: pvec, c: pvec, d: pvec):
    c_pmt_dgemv_n(A, b, c, d)
    return

# auxiliary functions
def pmt_set_data(M: pmat, data: POINTER(c_double)):
    c_pmt_set_blasfeo_dmat(M.blasfeo_dmat, data)  
    return

def pmat_set(M: pmat, value, i, j):
    c_pmt_set_blasfeo_dmat_el(value, M.blasfeo_dmat, i, j)  
    return

def pmat_get(M: pmat, i, j):
    el = c_pmt_get_blasfeo_dmat_el(M.blasfeo_dmat, i, j)  
    return el 

def pmat_print(M: pmat):
    c_pmt_print_blasfeo_dmat(M)
    return  


