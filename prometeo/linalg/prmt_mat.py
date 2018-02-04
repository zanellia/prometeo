from ctypes import *
from prmt_mat_blasfeo_wrapper import *
from blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat 
    
    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_prmt_mat(m, n)  
    
    def set(self, data: POINTER(c_double)):
        m = self.blasfeo_dmat.m 
        n = self.blasfeo_dmat.n 

        c_prmt_set_prmt_mat(self.blasfeo_dmat, data)  
    
    def print(self):
        c_prmt_print_prmt_mat(self)

def dgemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nt(A, B, C, D)


