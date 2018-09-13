
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
        for i in range(self.blasfeo_dmat.m):
            for j in range(self.blasfeo_dmat.n):
                self[i][j] = value
        return

    def copy(self, to_be_copied):
        for i in range(self.blasfeo_dmat.m):
            for j in range(self.blasfeo_dmat.n):
                value = to_be_copied[i][j]
                self[i][j] = value
        return
