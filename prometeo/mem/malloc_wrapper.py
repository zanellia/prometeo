from ctypes import *
import os
class malloc_wrapper:

    heap_db = {}
    use_prmt_heap = False
    
    def typed_alloc_p(self, type, n):
        mem_pointer = POINTER(c_double)()
        cwd = os.getcwd()
        malloc_wrapper = CDLL('%s/libmalloc_wrapper.so.0.1'%cwd)
        malloc_wrapper.prmt_malloc(byref(mem_pointer), n)
        return mem_pointer



