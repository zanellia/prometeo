from ctypes import *
from .pvec_blasfeo_wrapper import *
from .pmat_blasfeo_wrapper import *
from .pmat import *
from .blasfeo_wrapper import *
from abc import ABC

class pvec_(ABC):
    pass

class pvec(pvec_):
    # sizes in annotations of arguments, A: pmat[n, m], are for the checker
    @classmethod
    def __class_getitem__(cls, sizes):
        return cls


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

    def __array__(self, dtype=None, copy=None):
        # np.array(v): a copy of the vector as a NumPy array (see pmat)
        import numpy as np
        data = (c_double * self.m)()
        bw.blasfeo_unpack_dvec(self.m, self._ref, 0, data)
        return np.array(data, dtype=dtype)

    @property
    def T(self):
        return self

    def __mul__(self, other):
        if isinstance(other, pvec_):
            # elementwise product
            res = pvec(self.m)
            pvec_mul_view(1.0, self, 0, -1, other, 0, -1, res, 0, -1)
            return res
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

# z <= z + alpha * x .* y, elementwise (as c_pmt_pvec_mul_view)
def pvec_mul_view(alpha: float, x: pvec, xi: int, xr: int, y: pvec, yi: int, yr: int,
        z: pvec, zi: int, zr: int):
    xi, xr = _vview('pvec_mul', x, xi, xr)
    yi, yr = _vview('pvec_mul', y, yi, yr)
    zi, zr = _vview('pvec_mul', z, zi, zr)
    _same_length('pvec_mul', xr, yr, zr)
    get, put = bw.blasfeo_dvecex1, bw.blasfeo_dvecin1
    for i in range(zr):
        put(get(z._ref, zi + i) + alpha * (get(x._ref, xi + i) * get(y._ref, yi + i)), z._ref, zi + i)

# Rows A[i, j:j + r] and columns A[i:i + r, j] of matrices, copied to and from
# vectors (r = -1: to the end)
def _line(name, A, i, j, r, row):
    if r < 0:
        r = (A.n - j) if row else (A.m - i)
    end_i, end_j = (i + 1, j + r) if row else (i + r, j + 1)
    if i < 0 or j < 0 or r <= 0 or end_i > A.m or end_j > A.n:
        where = '[{}, {}:{}]'.format(i, j, j + r) if row else '[{}:{}, {}]'.format(i, i + r, j)
        raise IndexError('{}: {} out of range for a {}x{} pmat'.format(name, where, A.m, A.n))
    return r

def pmat_getrow_view(A, i: int, j: int, r: int, x: pvec, xi: int, xr: int):
    r = _line('pmat_getrow', A, i, j, r, True)
    xi, xr = _vview('pmat_getrow', x, xi, xr)
    _same_length('pmat_getrow', r, xr)
    bw.blasfeo_drowex(r, 1.0, A._ref, i, j, x._ref, xi)

def pmat_getcol_view(A, i: int, j: int, r: int, x: pvec, xi: int, xr: int):
    r = _line('pmat_getcol', A, i, j, r, False)
    xi, xr = _vview('pmat_getcol', x, xi, xr)
    _same_length('pmat_getcol', r, xr)
    bw.blasfeo_dcolex(r, A._ref, i, j, x._ref, xi)

def pmat_setrow_view(x: pvec, xi: int, xr: int, A, i: int, j: int, r: int):
    r = _line('pmat_setrow', A, i, j, r, True)
    xi, xr = _vview('pmat_setrow', x, xi, xr)
    _same_length('pmat_setrow', r, xr)
    bw.blasfeo_drowin(r, 1.0, x._ref, xi, A._ref, i, j)
    A.blasfeo_dmat.use_dA = 0

def pmat_setcol_view(x: pvec, xi: int, xr: int, A, i: int, j: int, r: int):
    r = _line('pmat_setcol', A, i, j, r, False)
    xi, xr = _vview('pmat_setcol', x, xi, xr)
    _same_length('pmat_setcol', r, xr)
    bw.blasfeo_dcolin(r, x._ref, xi, A._ref, i, j)
    A.blasfeo_dmat.use_dA = 0
