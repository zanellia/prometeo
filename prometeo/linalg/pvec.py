from ctypes import *
from .pvec_blasfeo_wrapper import *
from .pmat_blasfeo_wrapper import *
from .pmat import *
from .blasfeo_wrapper import *
from abc import ABC

class pvec_(ABC):
    pass

class pvec(pvec_):

    blasfeo_dvec = None

    def __init__(self, m: int):
        self.blasfeo_dvec = c_prmt_create_blasfeo_dvec(m)  
    
    def __getitem__(self, index):
        return pvec_get(self, index)

    def __setitem__(self, index, value):
        pvec_set(self, value, index)
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
def pvec_set_data(v: pvec, data: POINTER(c_double)):
    c_prmt_set_blasfeo_dvec(v.blasfeo_dvec, data)  

def pvec_set(v: pvec, value, i):
    c_prmt_set_blasfeo_dvec_el(value, v.blasfeo_dvec, i)  

def pvec_get(v: pvec, i):
    el = c_prmt_get_blasfeo_dvec_el(v.blasfeo_dvec, i)  
    return el 

def pvec_print(v: pvec):
    c_prmt_print_blasfeo_dvec(v)


