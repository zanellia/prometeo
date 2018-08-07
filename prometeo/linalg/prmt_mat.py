from ctypes import *
from .prmt_mat_blasfeo_wrapper import *
from .blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat 
    
    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_blasfeo_dmat(m, n)  
    
    def __getitem__(self, index):
        """ `self[row][col]` indexing and assignment. """
        return 


def prmt_set_data(M: prmt_mat, data: POINTER(c_double)):
    c_prmt_set_blasfeo_dmat(M.blasfeo_dmat, data)  

def prmt_set(M: prmt_mat, value, i, j):
    c_prmt_set_blasfeo_dmat_el(value, M.blasfeo_dmat, i, j)  

# def __getitem__(self, key):
#     """ `self[row][col]` indexing and assignment. """
#     return self.list[index]


def prmt_print(M: prmt_mat):
    c_prmt_print_blasfeo_dmat(M)

def prmt_gemm_nt(A: prmt_mat, B: prmt_mat, C: prmt_mat, D: prmt_mat):
    c_prmt_dgemm_nt(A, B, C, D)


