from ctypes import *
from .prmt_vec_blasfeo_wrapper import *
from .prmt_mat_blasfeo_wrapper import *
from .prmt_mat import *
from .blasfeo_wrapper import *

class prmt_vec:

    blasfeo_dvec = None

    def __init__(self, m: int):
        self.blasfeo_dvec = c_prmt_create_blasfeo_dvec(m)  
    
    def __getitem__(self, index):
        return prmt_vec_get(self, index)

    def __setitem__(self, index, value):
        prmt_vec_set(self, value, index)
        return
    
    def fill(self, value):
        for i in range(self.blasfeo_dvec.m):
            self[i] = value
        return

    def copy(self, to_be_copied):
        for i in range(self.blasfeo_dvec.m):
            value = to_be_copied[i]
            self[i] = value
        return

# auxiliary functions
def prmt_vec_set_data(v: prmt_vec, data: POINTER(c_double)):
    c_prmt_set_blasfeo_dvec(v.blasfeo_dvec, data)  

def prmt_vec_set(v: prmt_vec, value, i):
    c_prmt_set_blasfeo_dvec_el(value, v.blasfeo_dvec, i)  

def prmt_vec_get(v: prmt_vec, i):
    el = c_prmt_get_blasfeo_dvec_el(v.blasfeo_dvec, i)  
    return el 

def prmt_vec_print(v: prmt_vec):
    c_prmt_print_blasfeo_dvec(v)


