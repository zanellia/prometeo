from ctypes import *
from prmt_mat_blasfeo_wrapper import *
from blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat 
    
    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_blasfeo_dmat(m, n)  
    
    def set(self, data: POINTER(c_double)):
        m = self.blasfeo_dmat.m 
        n = self.blasfeo_dmat.n 

        c_prmt_set_blasfeo_dmat(self.blasfeo_dmat, data)  
    
    # def __getitem__(self, key):
    #     """ `self[row][col]` indexing and assignment. """
    #     return self.list[index]
    
    def __getitem__(self, index):
        """ `self[row][col]` indexing and assignment. """
        
        return 
    
    def print(self):
        c_prmt_print_blasfeo_dmat(self)

def dgemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nt(A, B, C, D)


