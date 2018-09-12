from .blasfeo_wrapper import *
from ctypes import *

def c_prmt_set_blasfeo_dmat(M, data: POINTER(c_double)):
         
    m = M.m
    n = M.n
    bw.blasfeo_pack_dmat(m, n, data, n, byref(M), 0, 0)

def c_prmt_set_blasfeo_dmat_el(value, M, ai, aj):
         
    bw.blasfeo_dgein1(value, byref(M), ai, aj)

def c_prmt_get_blasfeo_dmat_el(M, ai, aj):
         
    bw.blasfeo_dgeex1(byref(M), ai, aj)

def c_prmt_set_prmt_blasfeo_dmat(a, M, ai, aj):
         
    m = M.m
    n = M.n
    bw.blasfeo_pack_dmat(m, n, data, n, byref(M), 0, 0)

def c_prmt_create_blasfeo_dmat(m: int, n: int):
         
    size_strmat = bw.blasfeo_memsize_dmat(m, n)
    memory_strmat = c_void_p() 
    bw.v_zeros_align(byref(memory_strmat), size_strmat)

    ptr_memory_strmat = cast(memory_strmat, c_char_p)

    data = (POINTER(c_double) * 1)()
    bw.d_zeros(byref(data), n, n)

    sA = blasfeo_dmat()

    bw.blasfeo_allocate_dmat(m, n, byref(sA))
    bw.blasfeo_create_dmat(m, n, byref(sA), ptr_memory_strmat)
    bw.blasfeo_pack_dmat(m, n, data, n, byref(sA), 0, 0)
    return sA

# low-level linear algebra
def c_prmt_dgemm_nn(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_nn(bA.m, bA.n, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)

def c_prmt_dgemm_nt(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_nt(bA.m, bA.n, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)

def c_prmt_dgemm_tn(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_tn(bA.m, bA.n, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)

def c_prmt_dgemm_tt(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_tt(bA.m, bA.n, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)

def c_prmt_dgead(alpha, A, B, C):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat

    bw.blasfeo_dgead(bA.m, bA.n, alpha, byref(bA), 0, 0, byref(bC), 0, 0)

# auxiliary functions
def c_prmt_print_blasfeo_dmat(A):
    bw.blasfeo_print_dmat(A.blasfeo_dmat.m, A.blasfeo_dmat.n, byref(A.blasfeo_dmat), 0, 0)

       
