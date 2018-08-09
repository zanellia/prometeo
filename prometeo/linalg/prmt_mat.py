from ctypes import *
from .prmt_mat_blasfeo_wrapper import *
from .blasfeo_wrapper import *

class prmt_mat:

    blasfeo_dmat = None
    _i = None
    _j = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_blasfeo_dmat(m, n)  
    
    def __getitem__(self, index):
        if self._i is not None:
            self._j = index
            self.my_get_item()
            return

        self._i = index
        return self

    def __setitem__(self, index, value):
        self._j = index
        self.my_set_item(value)
        return
   

    def my_set_item(self, value):
        prmt_set(self, value, self._i, self._j)
        self._i = None
        self._j = None
        return

    def my_get_item(self):
        print(self._i, self._j)
        self._i = None
        self._j = None
        return
    def __call__(self, i, j):
        self.set_get_i = i
        self.set_get_j = j
        return self.set_get_attr  

    def __setattr__(self, name, value):
        if name == 'set_get_attr':
            c_prmt_set_blasfeo_dmat_el(value, self.blasfeo_dmat, set_get_i, set_get_j)  
        else:
            super(prmt_mat, self).__setattr__(name, value)

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


