
from ctypes import *
from .prmt_mat_blasfeo_wrapper import *
from .blasfeo_wrapper import *

class prmt_vec:

    blasfeo_dvec = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_prmt_create_blasfeo_dmat(m, n)  
    
    def __getitem__(self, index):
        if self._i is not None:
            self._j = index
            el = self.my_get_item()
            return el

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
        el = prmt_get(self, self._i, self._j)
        self._i = None
        self._j = None
        return el 
    
    def fill(self, value):
        for i in range(self.blasfeo_dvec.m):
            self[i] = value
        return

    def copy(self, to_be_copied):
        for i in range(self.blasfeo_dmat.m):
                value = to_be_copied[i]
                self[i] = value
        return

# auxiliary functions
def prmt_set_data(v: prmt_vec, data: POINTER(c_double)):
    c_prmt_set_blasfeo_dvec(v.blasfeo_dvec, data)  

def prmt_set(v: prmt_vec, value, i):
    c_prmt_set_blasfeo_dvec_el(value, v.blasfeo_dvec, i)  

def prmt_get(v: prmt_vec, i):
    el = c_prmt_get_blasfeo_dmat_el(v.blasfeo_dvec, i)  
    return el 

def prmt_print(v: prmt_vec):
    c_prmt_print_blasfeo_dvec(v)


