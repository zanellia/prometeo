from ctypes import *
from os import *

class blasfeo_dmat(Structure):
    _fields_ = [    ("m", c_int),
	            ("n", c_int),
	            ("pm", c_int),
	            ("cn", c_int),
	            ("pA", POINTER(c_double)),
	            ("dA", POINTER(c_double)),
	            ("use_dA", c_int),
	            ("memsize", c_int)]

cwd = getcwd()
bw = CDLL('%s/../../external/blasfeo/lib/libblasfeo.so' %cwd)

bw.blasfeo_dgemm_nt.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

def blasfeo_dgemm_nt(m: c_int, n: c_int, k: c_int, alpha: c_double, 
                     sA: POINTER(blasfeo_dmat), ai: c_int, aj: c_int, 
                     sB: POINTER(blasfeo_dmat), bi: c_int, bj: c_int, 
                     beta: c_double, sC: POINTER(blasfeo_dmat), 
                     ci: c_int, cj: c_int, sD: POINTER(blasfeo_dmat), 
                     di: c_int, dj: c_int):
    
    bw.blasfeo_dgemm_nt(m, n, k, alpha, byref(sA), ai, aj, byref(sB), bi, bj, beta, 
                        sC, ci, cj, byref(sD), di, dj)

