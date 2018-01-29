from ctypes import *
from prmt_mat_blasfeo_wrapper import *
from blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat 
    
#    def __init__(self, m: int, n: int, data: POINTER(c_double)):
#        self.blasfeo_dmat = c_prmt_create_prmt_mat(m, n, data)  
    
    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_prmt_mat(m, n)  
    
    def print(self):
        c_prmt_print_prmt_mat(self)

def dgemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nt(A, B, C, D)


