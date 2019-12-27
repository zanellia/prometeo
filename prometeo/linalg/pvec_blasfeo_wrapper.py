from .blasfeo_wrapper import *
from ctypes import *

def c_pmt_set_blasfeo_dvec(v, data: POINTER(c_double)):
         
    m = v.m
    bw.blasfeo_pack_dvec(m, data, byref(v), 0)

def c_pmt_set_blasfeo_dvec_el(value, v, ai):
         
    bw.blasfeo_dvecin1(value, byref(v), ai);

def c_pmt_get_blasfeo_dvec_el(v, ai):
         
    el = bw.blasfeo_dvecex1(byref(v), ai)
    return el 

def c_pmt_set_pmt_blasfeo_dvec(data, v, ai):
         
    m = v.m
    bw.blasfeo_pack_dvec(m, data, byref(v), 0)

def c_pmt_create_blasfeo_dvec(m: int):
         
    size_strvec = bw.blasfeo_memsize_dvec(m)
    memory_strvec = c_void_p() 
    bw.v_zeros_align(byref(memory_strvec), size_strvec)

    ptr_memory_strvec = cast(memory_strvec, c_char_p)

    data = (POINTER(c_double) * 1)()
    bw.d_zeros(byref(data), m, 1)

    sv = blasfeo_dvec()

    bw.blasfeo_allocate_dvec(m, byref(sv))
    bw.blasfeo_create_dvec(m, byref(sv), ptr_memory_strvec)
    bw.blasfeo_pack_dvec(m, data, byref(sv), 0)
    # initialize to 0.0
    bw.blasfeo_dvecse(m, 0.0, byref(sv), 0);
    return sv

def c_pmt_vecpe(m, ipiv, a):
    ba = a.blasfeo_dvec
    bw.blasfeo_dvecpe(m, ipiv, byref(ba));
    return

# auxiliary functions
def c_pmt_print_blasfeo_dvec(v):
    bw.blasfeo_print_dvec(v.blasfeo_dvec.m, byref(v.blasfeo_dvec), 0)
