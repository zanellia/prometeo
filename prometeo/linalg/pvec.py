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
       self._m = m
       self.blasfeo_dvec = c_pmt_create_blasfeo_dvec(m)  
       # reference passed to BLASFEO, created once
       self._ref = byref(self.blasfeo_dvec)
    
    @property
    def m(self):
        return self._m

    def check_index(self, index):
        if index < 0 or index >= self.m:
            raise IndexError('index {} out of range for a pvec of size {}'.format(index, self.m))

    def __getitem__(self, index):
        self.check_index(index)
        return pvec_get(self, index)

    def __setitem__(self, index, value):
        self.check_index(index)
        pvec_set(self, value, index)
        return
    
    # high-level linear algebra, as in NumPy (allocating the result)
    def __matmul__(self, other):
        if isinstance(other, pvec_):
            return pvec_dot_view(self, 0, -1, other, 0, -1)
        res = pvec(other.n)
        pmt_gemv_view_t(1.0, other, 0, 0, -1, -1, self, 0, -1, 1.0, res, 0, -1, res, 0, -1)
        return res

    @property
    def T(self):
        return self

    def __mul__(self, other):
        if isinstance(other, pvec_):
            raise TypeError("'*' between vectors is the elementwise product (as in NumPy), "
                "which is not supported: use '@' for the dot product")
        res = pvec(self.m)
        pvec_copy_view(self, 0, -1, res, 0, -1)
        pvec_scale_view(float(other), res, 0, -1)
        return res

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * (1.0 / other)

    def __neg__(self):
        return self * -1.0

    def __add__(self, other):
        res = pvec(self.m)
        pvec_copy_view(self, 0, -1, res, 0, -1)
        pvec_axpy_view(1.0, other, 0, -1, res, 0, -1)
        return res

    def __sub__(self, other):
        res = pvec(self.m)
        pvec_copy_view(self, 0, -1, res, 0, -1)
        pvec_axpy_view(-1.0, other, 0, -1, res, 0, -1)
        return res

    def fill(self, value):
        for i in range(self.blasfeo_dvec.m):
            self[i] = value
        return

    def copy(self, to_be_copied):
        for i in range(self.blasfeo_dvec.m):
            value = to_be_copied[i]
            self[i] = value
        return

def pmt_vecpe(m, ipiv, a):
    c_pmt_vecpe(m, ipiv, a)

# auxiliary functions
def pvec_set_data(v: pvec, data: POINTER(c_double)):
    c_pmt_set_blasfeo_dvec(v.blasfeo_dvec, data)  

def pvec_set(v: pvec, value, i):
    c_pmt_set_blasfeo_dvec_el(value, v.blasfeo_dvec, i)  

def pvec_get(v: pvec, i):
    el = c_pmt_get_blasfeo_dvec_el(v.blasfeo_dvec, i)  
    return el 

def pvec_print(v: pvec):
    c_pmt_print_blasfeo_dvec(v)

def pvec_copy(a: pvec, b: pvec):
    for i in range(a.blasfeo_dvec.m):
        b[i] = a[i]
    return



# Vectors and slices of vectors, used by vector expressions: a slice v[a:b]
# is passed as v, a, b - a, a whole vector as v, 0, -1.
def _vview(name, v, i, r):
    if r < 0:
        r = v.m - i
    if i < 0 or r <= 0 or i + r > v.m:
        raise IndexError('{}: slice [{}:{}] out of range for a pvec of size {}'.format(
            name, i, i + r, v.m))
    return i, r

def _same_length(name, *sizes):
    if len(set(sizes)) != 1:
        raise Exception('{}: mismatching dimensions: {}'.format(name, ', '.join(map(str, sizes))))

def pvec_copy_view(x: pvec, xi: int, xr: int, y: pvec, yi: int, yr: int):
    xi, xr = _vview('pvec_copy', x, xi, xr)
    yi, yr = _vview('pvec_copy', y, yi, yr)
    _same_length('pvec_copy', xr, yr)
    bw.blasfeo_dveccp(xr, x._ref, xi, y._ref, yi)

def pvec_fill_view(value: float, x: pvec, xi: int, xr: int):
    xi, xr = _vview('pvec_fill', x, xi, xr)
    bw.blasfeo_dvecse(xr, value, x._ref, xi)

def pvec_scale_view(alpha: float, x: pvec, xi: int, xr: int):
    xi, xr = _vview('pvec_scale', x, xi, xr)
    bw.blasfeo_dvecsc(xr, alpha, x._ref, xi)

# y <= y + alpha * x
def pvec_axpy_view(alpha: float, x: pvec, xi: int, xr: int, y: pvec, yi: int, yr: int):
    xi, xr = _vview('pvec_axpy', x, xi, xr)
    yi, yr = _vview('pvec_axpy', y, yi, yr)
    _same_length('pvec_axpy', xr, yr)
    bw.blasfeo_daxpy(xr, alpha, x._ref, xi, y._ref, yi, y._ref, yi)

def pvec_dot_view(x: pvec, xi: int, xr: int, y: pvec, yi: int, yr: int) -> float:
    xi, xr = _vview('pvec_dot', x, xi, xr)
    yi, yr = _vview('pvec_dot', y, yi, yr)
    _same_length('pvec_dot', xr, yr)
    return bw.blasfeo_ddot(xr, x._ref, xi, y._ref, yi)

# z <= beta * y + alpha * op(A) x
def _gemv_view(t, alpha, A, ai, aj, ar, ac, x, xi, xr, beta, y, yi, yr, z, zi, zr):
    # pmat.py imports this module
    from .pmat import _view
    name = 'pmt_gemv_' + t
    ai, aj, ar, ac = _view(name, A, ai, aj, ar, ac)
    xi, xr = _vview(name, x, xi, xr)
    yi, yr = _vview(name, y, yi, yr)
    zi, zr = _vview(name, z, zi, zr)
    m, n = (ac, ar) if t == 't' else (ar, ac)
    if xr != n or yr != m or zr != m:
        raise Exception('{}: mismatching dimensions: ({}, {}){} x ({}) -> ({}), ({})'.format(
            name, ar, ac, '^T' if t == 't' else '', xr, yr, zr))
    getattr(bw, 'blasfeo_dgemv_' + t)(ar, ac, alpha, A._ref, ai, aj, x._ref, xi,
        beta, y._ref, yi, z._ref, zi)

def pmt_gemv_view_n(alpha: float, A, ai: int, aj: int, ar: int, ac: int,
        x: pvec, xi: int, xr: int, beta: float, y: pvec, yi: int, yr: int, z: pvec, zi: int, zr: int):
    _gemv_view('n', alpha, A, ai, aj, ar, ac, x, xi, xr, beta, y, yi, yr, z, zi, zr)

def pmt_gemv_view_t(alpha: float, A, ai: int, aj: int, ar: int, ac: int,
        x: pvec, xi: int, xr: int, beta: float, y: pvec, yi: int, yr: int, z: pvec, zi: int, zr: int):
    _gemv_view('t', alpha, A, ai, aj, ar, ac, x, xi, xr, beta, y, yi, yr, z, zi, zr)

# x <= (L L^T)^-1 x, L lower triangular (not modified)
def pmt_potrsv_view(L, x: pvec, xi: int, xr: int):
    xi, xr = _vview('pmt_potrsv', x, xi, xr)
    if L.m != L.n or L.m != xr:
        raise Exception('pmt_potrsv: mismatching dimensions: ({}, {}) \\ ({})'.format(L.m, L.n, xr))
    bw.blasfeo_dtrsv_lnn(xr, L._ref, 0, 0, x._ref, xi, x._ref, xi)
    bw.blasfeo_dtrsv_ltn(xr, L._ref, 0, 0, x._ref, xi, x._ref, xi)

def cho_solve_vec(L, b: pvec):
    x = pvec(b.m)
    pvec_copy_view(b, 0, -1, x, 0, -1)
    pmt_potrsv_view(L, x, 0, -1)
    return x
