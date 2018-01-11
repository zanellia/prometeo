from ctypes import *
from os import *
from blasfeo_wrapper import *


#ctypes seems to be struggling with arg types of the dgemm routine:
bw.blasfeo_dgemm_nt.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

n = 5 

size_strmat = 100*bw.blasfeo_memsize_dmat(n, n)
memory_strmat = c_void_p() 
bw.v_zeros_align(byref(memory_strmat), size_strmat)

ptr_memory_strmat = cast(memory_strmat, c_char_p)

A = (POINTER(c_double) * 1)()
bw.d_zeros(byref(A), n, n)
for i in range(n*n):
    A[0][i] = i

sA = blasfeo_dmat()

bw.blasfeo_allocate_dmat(n, n, byref(sA))
bw.blasfeo_create_dmat(n, n, byref(sA), ptr_memory_strmat)
bw.blasfeo_pack_dmat(n, n, A[0], n, byref(sA), 0, 0);
bw.blasfeo_print_dmat(n, n, byref(sA), 0, 0)

ptr_memory_strmat = cast(ptr_memory_strmat, c_void_p)
ptr_memory_strmat.value = ptr_memory_strmat.value + sA.memsize
ptr_memory_strmat = cast(ptr_memory_strmat, c_char_p)

D = (POINTER(c_double) * 1)()
bw.d_zeros(byref(D), n, n)
for i in range(n):
    D[0][i*(n + 1)] = 1.0

sD = blasfeo_dmat()

bw.blasfeo_allocate_dmat(n, n, byref(sD))
bw.blasfeo_create_dmat(n, n, byref(sD), ptr_memory_strmat)
bw.blasfeo_pack_dmat(n, n, D[0], n, byref(sD), 0, 0);
bw.blasfeo_print_dmat(n, n, byref(sD), 0, 0)

ptr_memory_strmat = cast(ptr_memory_strmat, c_void_p)
ptr_memory_strmat.value = ptr_memory_strmat.value + sD.memsize
ptr_memory_strmat = cast(ptr_memory_strmat, c_char_p)

B = (POINTER(c_double) * 1)()
bw.d_zeros(byref(B), n, n)
for i in range(n):
    B[0][i*(n + 1)] = 1.0

sB = blasfeo_dmat()

bw.blasfeo_allocate_dmat(n, n, byref(sB))
bw.blasfeo_create_dmat(n, n, byref(sB), ptr_memory_strmat)
bw.blasfeo_pack_dmat(n, n, B[0], n, byref(sB), 0, 0);
bw.blasfeo_print_dmat(n, n, byref(sB), 0, 0)

ptr_memory_strmat = cast(ptr_memory_strmat, c_void_p)
ptr_memory_strmat.value = ptr_memory_strmat.value + sB.memsize
ptr_memory_strmat = cast(ptr_memory_strmat, c_char_p)

#bw.blasfeo_dgemm_nt(n, n, n, 1.0, byref(sA), 0, 0, byref(sA), 0, 0, 1, byref(sB), 0, 0, byref(sD), 0, 0);
blasfeo_dgemm_nt(n, n, n, 1.0, sA, 0, 0, sA, 0, 0, 1, sB, 0, 0, sD, 0, 0);
bw.blasfeo_print_dmat(n, n, byref(sD), 0, 0)

