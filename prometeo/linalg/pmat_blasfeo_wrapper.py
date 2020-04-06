from .blasfeo_wrapper import *
from ctypes import *


bw.blasfeo_dgeex1.restype = c_double     
# bw.blasfeo_dgead.argtypes = [c_int, c_int, double     
# void blasfeo_dgead(int m, int n, double alpha, struct blasfeo_dmat *sA, int ai, int aj, struct blasfeo_dmat *sC, int yi, int cj);

def c_pmt_set_blasfeo_dmat(M, data: POINTER(c_double)):
         
    m = M.m
    n = M.n
    bw.blasfeo_pack_dmat(m, n, data, n, byref(M), 0, 0)

def c_pmt_set_blasfeo_dmat_el(value, M, ai, aj):
         
    bw.blasfeo_dgein1(value, byref(M), ai, aj)

def c_pmt_get_blasfeo_dmat_el(M, ai, aj):
    el = bw.blasfeo_dgeex1(byref(M), ai, aj)
    return el 

def c_pmt_set_pmt_blasfeo_dmat(data, M, ai, aj):
         
    m = M.m
    n = M.n
    bw.blasfeo_pack_dmat(m, n, data, n, byref(M), 0, 0)

def c_pmt_create_blasfeo_dmat(m: int, n: int):
         
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
    # initialize to 0.0
    bw.blasfeo_dgese(m, n, 0.0, byref(sA), 0, 0);
    return sA

# TODO(andrea): move body of these functions directly 
# inside the intermediate-level and make those the
# low-level

# intermediate-level linear algebra
def c_pmt_dgemm_nn(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_nn(bA.m, bB.n, bA.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)
    return

def c_pmt_dgemm_nt(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_nt(bA.m, bA.n, bB.m, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)
    return

def c_pmt_dgemm_tn(A, B, C, D):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    bC = C.blasfeo_dmat
    bD = D.blasfeo_dmat

    bw.blasfeo_dgemm_tn(bA.n, bB.n, bA.m, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)
    return

# def c_pmt_dgemm_tt(A, B, C, D):
#     bA = A.blasfeo_dmat
#     bB = B.blasfeo_dmat
#     bC = C.blasfeo_dmat
#     bD = D.blasfeo_dmat

#     bw.blasfeo_dgemm_tt(bA.m, bA.n, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, 1, byref(bC), 0, 0, byref(bD), 0, 0)
#     return

def c_pmt_dgead(alpha, A, B):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat

    bw.blasfeo_dgead(bA.m, bA.n, alpha, byref(bA), 0, 0, byref(bB), 0, 0)
    return

def c_pmt_drowpe(m, ipiv, A):
    bA = A.blasfeo_dmat
    bw.blasfeo_drowpe(m, ipiv, byref(bA));
    return

def c_pmt_getrf(A, fact, ipiv):
    bA = A.blasfeo_dmat
    bfact = fact.blasfeo_dmat
    bw.blasfeo_dgetrf_rp(bA.m, bA.m, byref(bA), 0, 0, byref(bfact), 0, 0, ipiv)
    return

def c_pmt_potrf(A, fact):
    bA = A.blasfeo_dmat
    bfact = fact.blasfeo_dmat

    bw.blasfeo_dpotrf_l(bA.m, byref(bA), 0, 0, byref(bfact), 0, 0)
    return

def c_pmt_trsm_llnn(A, B):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    
    bw.blasfeo_dtrsm_llnn(bB.m, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, byref(bB), 0, 0)
    return

def c_pmt_trsm_llnu(A, B):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    
    bw.blasfeo_dtrsm_llnu(bB.m, bB.n, 1.0, byref(bA), 0, 0, byref(bB), 0, 0, byref(bB), 0, 0)
    return

def c_pmt_trsm_lunn(A, B):
    bA = A.blasfeo_dmat
    bB = B.blasfeo_dmat
    
    bw.blasfeo_dtrsm_lunn(bB.m, bB.n, 1.0, byref(bA), 0, 0, byref(bB), \
            0, 0, byref(bB), 0, 0)
    return

def c_pmt_trsv_llnu(A, b):
    bA = A.blasfeo_dmat
    bb = b.blasfeo_dvec
    
    bw.blasfeo_dtrsv_lnn(bb.m, 1.0, byref(bA), 0, 0, byref(bb), 0, byref(bb), 0)
    return

def c_pmt_trsv_lunn(A, b):
    bA = A.blasfeo_dmat
    bb = b.blasfeo_dvec    

    bw.blasfeo_dtrsv_lnn(bb.m, 1.0, byref(bA), 0, 0, byref(bb), \
            0, byref(bb), 0)
    return

def c_pmt_dgemv_n(A, b, c, d):
    bA = A.blasfeo_dmat
    bb = b.blasfeo_dvec
    bc = c.blasfeo_dvec
    bd = d.blasfeo_dvec

    bw.blasfeo_dgemv_n(bA.m, bA.n, 1.0, byref(bA), 0, 0, byref(bb), 0, \
            1.0, byref(bc), 0, byref(bd), 0)
    return

# auxiliary functions
def c_pmt_print_blasfeo_dmat(A):
    bw.blasfeo_print_dmat(A.m, A.n, byref(A.blasfeo_dmat), 0, 0)
    return

       
