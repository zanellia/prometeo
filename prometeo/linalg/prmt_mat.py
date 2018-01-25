from ctypes import *
import prmt_mat_blasfeo_wrapper

class prmt_mat:
   
    self.m: int
    self.n: int 
    self.data: prmt_real_p

    def __init__(self, m: int, n: int, data: POINTER(c_double)):
        ___c_prmt___create_prmt_mat(m, n, data)  
    
def dgemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat):
    ___c_prmt___dgemm_nt(A, B, C)




