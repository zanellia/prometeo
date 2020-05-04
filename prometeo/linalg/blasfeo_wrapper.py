from ctypes import *
import os

bw = CDLL(os.path.dirname(__file__) + '/../lib/blasfeo/libblasfeo.so')

class blasfeo_dmat(Structure):
    _fields_ = [    ("m", c_int),
	            ("n", c_int),
	            ("pm", c_int),
	            ("cn", c_int),
	            ("pA", POINTER(c_double)),
	            ("dA", POINTER(c_double)),
	            ("use_dA", c_int),
	            ("memsize", c_int)]

class blasfeo_dvec(Structure):
    _fields_ = [    ("m", c_int),
	            ("pm", c_int),
	            ("pa", POINTER(c_double)),
	            ("memsize", c_int)]

bw.blasfeo_dgemm_nn.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgemm_nt.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgemm_tn.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgemm_tt.argtypes = [c_int, c_int, c_int, c_double, 
    POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
    c_double, POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgead.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgein1.argtypes = [c_double, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dgeex1.argtypes = [POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_drowpe.argtypes = [c_int, POINTER(c_int), POINTER(blasfeo_dmat)]

bw.blasfeo_dgetrf_rp.argtypes = [c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dmat), c_int, c_int, POINTER(c_int)]

bw.blasfeo_dtrsm_llnn.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dtrsm_llnu.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dtrsm_lunn.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dmat), c_int, c_int, POINTER(blasfeo_dmat), c_int, c_int]

bw.blasfeo_dtrsv_lnn.argtypes = [c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dvec), c_int, POINTER(blasfeo_dvec), c_int]

bw.blasfeo_dtrsv_lnn.argtypes = [c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dvec), c_int, POINTER(blasfeo_dvec), c_int]

bw.blasfeo_dgemv_n.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int, 
        POINTER(blasfeo_dvec), c_int, c_double, POINTER(blasfeo_dvec), c_int, POINTER(blasfeo_dvec), c_int]


bw.blasfeo_dgese.argtypes = [c_int, c_int, c_double, POINTER(blasfeo_dmat), c_int, c_int]
bw.blasfeo_dvecse.argtypes = [c_int, c_double, POINTER(blasfeo_dvec), c_int]
# def blasfeo_dgemm_nt(m: c_int, n: c_int, k: c_int, alpha: c_double, 
#                      sA: POINTER(blasfeo_dmat), ai: c_int, aj: c_int, 
#                      sB: POINTER(blasfeo_dmat), bi: c_int, bj: c_int, 
#                      beta: c_double, sC: POINTER(blasfeo_dmat), 
#                      ci: c_int, cj: c_int, sD: POINTER(blasfeo_dmat), 
#                      di: c_int, dj: c_int):

#     bw.blasfeo_dgemm_nt(m, n, k, alpha, byref(sA), ai, aj, byref(sB), bi, bj, beta, 
#                         byref(sC), ci, cj, byref(sD), di, dj)

# blasfeo_dvec

bw.blasfeo_dvecin1.argtypes = [c_double, POINTER(blasfeo_dvec), c_int]
bw.blasfeo_dvecex1.restype = c_double 
