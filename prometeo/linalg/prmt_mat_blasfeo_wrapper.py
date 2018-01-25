from blasfeo_wrapper import *
from ctypes import *

def ___c_prmt___create_prmt_mat(m: int, n: int, data: POINTER(c_double)):
         
    size_strmat = bw.blasfeo_memsize_dmat(m, n)
    memory_strmat = c_void_p() 
    bw.v_zeros_align(byref(memory_strmat), size_strmat)

    ptr_memory_strmat = cast(memory_strmat, c_char_p)

    A = (POINTER(c_double) * 1)()
    bw.d_zeros(byref(A), n, n)

    sA = blasfeo_dmat()

    bw.blasfeo_allocate_dmat(n, n, byref(sA))
    bw.blasfeo_create_dmat(n, n, byref(sA), ptr_memory_strmat)
    bw.blasfeo_pack_dmat(n, n, A[0], n, byref(sA), 0, 0)

def ___c_prmt___dgemm_nt(A, B, C):

