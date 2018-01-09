from ctypes import *
import os
def prmt_malloc(n_bytes):
    mem_pointer = c_void_p()
    cwd = os.getcwd()
    malloc_wrapper = CDLL('%s/libmalloc_wrapper.so.0.1'%cwd)
    malloc_wrapper.prmt_malloc(byref(mem_pointer), n_bytes)
    return mem_pointer


def prmt_cast_to_double_p(pointer):
    return cast(pointer, POINTER(c_double))

def prmt_cast_to_int_p(pointer):
    return cast(pointer, POINTER(c_int))

