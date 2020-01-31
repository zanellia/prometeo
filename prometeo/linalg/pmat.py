from ctypes import *
from .pmat_blasfeo_wrapper import *
from .pvec import *
from .blasfeo_wrapper import *
from multipledispatch import dispatch
from abc import ABC

class pmat_(ABC):
    pass

class pmat(pmat_):
    blasfeo_dmat = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_pmt_create_blasfeo_dmat(m, n)
        self._m = m
        self._n = n

    @property
    def m(self):
        return self._m

    @property
    def n(self):
        return self._n

    def __getitem__(self, index):
        if isinstance(index, tuple):
            if len(index) != 2:
                raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                        you have: {}\n. Exiting'.format(index))
            if isinstance(index[0], int) and isinstance(index[1], int):
                if index[0] < 0 or index[0] > self.m or \
                        index[1] < 0 or index[1] > self.n:
                    raise Exception('Invalid subscripting values. Exiting. \n')
                el = pmat_get(self, index[0], index[1])
                return el
            elif isinstance(index[0], slice) and isinstance(index[1], slice):
                if index[0].start < 0 or index[0].stop > self.m or \
                    index[1].start < 0 or index[1].stop > self.n:
                        raise Exception('Invalid subscripting values. Exiting. \n')
                m_value = index[0].stop - index[0].start
                n_value = index[1].stop - index[1].start
                submatrix = pmat(m_value, n_value)
                # TODO(andrea): there might be better performing implementations of this.
                # print(index[0].start)
                # import pdb; pdb.set_trace()
                for i in range(m_value):
                    for j in range(n_value):
                        # print(i,j)
                        submatrix[i,j] = self[index[0].start+i, index[1].start+j]
                # print('\n\n')
                # pmat_print(submatrix)
                # print('\n\n')
                return submatrix
        else:
            raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                    you have: {}\n. Exiting'.format(index))

    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            if len(index) != 2:
                raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                        you have: {}\n. Exiting'.format(index))
            if isinstance(index[0], int) and isinstance(index[1], int):
                if index[0] < 0 or index[0] > self.m or \
                        index[1] < 0 or index[1] > self.n:
                    raise Exception('Invalid subscripting values. Exiting. \n')
                pmat_set(self, value, index[0], index[1])
            elif isinstance(index[0], slice) and isinstance(index[1], slice):
                m_target = index[0].stop - index[0].start
                n_target = index[1].stop - index[1].start
                if m_target != value.m or n_target != value.n:
                    raise Exception('Dimension mismatch: ({},{}) <- ({},{}). Exiting.'.format(m_target, n_target, value.m, value.n))
                if index[0].start < 0 or index[0].stop > self.m or \
                    index[1].start < 0 or index[1].stop > self.n:
                        raise Exception('Invalid subscripting values. Exiting. \n')
                # TODO(andrea): there might be better performing implementations of this.
                for i in range(m_target):
                    for j in range(n_target):
                        self[index[0].start+i,index[1].start+j] = value[i,j]
            else:
                raise Exception ('pmat subscripts must be 2-dimensional tuples, \
                        you have: {}\n. Exiting'.format(index))
        else:
            raise Exception ('pmat subscripts must be 2-dimensional tuples, \
                    you have: {}\n. Exiting'.format(index))

# class pmat(pmat_):

#     blasfeo_dmat = None
#     _i = None
#     _j = None

#     def __init__(self, m: int, n: int):
#         self.blasfeo_dmat = c_pmt_create_blasfeo_dmat(m, n)

#     def __getitem__(self, index):
#         if self._i is not None:
#             self._j = index
#             el = self.my_get_item()
#             return el

#         self._i = index
#         return self

#     def __setitem__(self, index, value):
#         self._j = index
#         self.my_set_item(value)
#         return


#     def my_set_item(self, value):
#         pmat_set(self, value, self._i, self._j)
#         self._i = None
#         self._j = None
#         return

#     def my_get_item(self):
#         el = pmat_get(self, self._i, self._j)
#         self._i = None
#         self._j = None
#         return el

    # TODO(andrea): ideally one would have three levels:
    # 1) high-level
    # 2) intermediate-level
    # 3) low-level (BLASFEO wrapper)

    # high-level linear algebra
    @dispatch(pmat_)
    def __mul__(self, other):
        if self.n != other.m:
            raise Exception('__mul__: mismatching dimensions:'
                ' ({}, {}) x ({}, {})'.format(self.m, self.n, other.m, other.n))

        res = pmat(self.m, other.n)
        pmat_fill(res, 0.0)
        zero_mat = pmat(self.m, other.n)
        pmat_fill(zero_mat, 0.0)
        pmt_gemm_nn(self, other, zero_mat, res)
        return res

    @dispatch(pvec_)
    def __mul__(self, other):
        if self.n != other.blasfeo_dvec.m:
            raise Exception('__mul__: mismatching dimensions:'
                ' ({}, {}) x ({},)'.format(self.m, self.n, other.blasfeo_dvec.m))

        res = pvec(self.m)
        res.fill(0.0)
        zero_vec = pvec(self.m)
        zero_vec.fill(0.0)
        pmt_gemv_n(self, other, zero_vec, res)
        return res

    @dispatch(pmat_)
    def __add__(self, other):
        if self.m != other.m or self.n != other.n:
            raise Exception('__add__: mismatching dimensions:'
                ' ({}, {}) + ({}, {})'.format(self.m, self.n, other.m, other.n))
        res = pmat(self.m, self.n)
        pmat_copy(other, res)
        pmt_gead(1.0, self, res)
        return res

    def __sub__(self, other):
        if self.m != other.m or self.n != other.n:
            raise Exception('__sub__: mismatching dimensions:'
                ' ({}, {}) + ({}, {})'.format(self.m, self.n, other.m, other.n))
        res = pmat(self.m, self.n)
        pmat_copy(self, res)
        pmt_gead(-1.0, other, res)
        return res

def pmat_fill(A: pmat, value: float):
    for i in range(A.m):
        for j in range(A.n):
            A[i,j] = value
    return

def pmat_copy(A: pmat, B: pmat):
    if A.m != B.m or A.n != B.n:
        raise Exception('__copy__: mismatching dimensions:'
            ' ({}, {}) -> ({}, {})'.format(A.m, A.n, B.m, B.n))
    for i in range(A.m):
        for j in range(A.n):
            B[i,j] = A[i,j]
    return

def pmat_tran(A: pmat, B: pmat):
    if A.m != B.n or A.n != B.m:
        raise Exception('__tran__: mismatching dimensions:'
            ' ({}, {}) -> ({}, {})'.format(A.m, A.n, B.m, B.n))
    for i in range(A.m):
        for j in range(A.n):
            B[j,i] = A[i,j]

def pmat_vcat(A: pmat, B: pmat, res: pmat):
    if A.n != B.n or A.n != res.n or A.m + B.m != res.m:
        raise Exception('__vcat__: mismatching dimensions:'
            ' ({}, {}) ; ({}, {})'.format(A.m, A.n, B.m, B.n))
    for i in range(A.m):
        for j in range(A.n):
            res[i,j] = A[i,j]
    for i in range(B.m):
        for j in range(B.n):
            res[A.m + i,j] = B[i,j]

def pmat_hcat(A: pmat, B: pmat, res: pmat):
    if A.m != B.m or A.m != res.m or A.n + B.n != res.n:
        raise Exception('__hcat__: mismatching dimensions:'
            ' ({}, {}) , ({}, {})'.format(A.m, A.n, B.m, B.n))
    for i in range(A.m):
        for j in range(A.n):
            res[i,j] = A[i,j]
    for i in range(B.m):
        for j in range(B.n):
            res[i,A.n + j] = B[i,j]

# def pmt_getrsm(fact: pmat, ipiv: list, rhs: pmat):
#     # create permutation vector
#     c_ipiv = cast(create_string_buffer(sizeof(c_int)*A.m), POINTER(c_int))
#     for i in range(A.n):
#         c_ipiv[i] = ipiv[i]
#     res  = pmat(A.m, B.n)
#     # create permuted rhs
#     # pB = pmat(B.m, B.n)
#     pmat_copy(B, res)
#     pmt_rowpe(B.m, c_ipiv, res)
#     # solve
#     pmt_trsm_llnu(A, res)
#     pmt_trsm_lunu(A, res)
#     return res

# def pmt_getrsv(fact: pmat, ipiv: list, rhs: pvec):
#     # create permutation vector
#     c_ipiv = cast(create_string_buffer(sizeof(c_int)*fact.m), POINTER(c_int))
#     for i in range(fact.n):
#         c_ipiv[i] = ipiv[i]
#     # permuted rhs
#     pvec_copy(b, res)
#     pmt_vecpe(b.blasfeo_dvec.m, c_ipiv, res)
#     # solve
#     pmt_trsv_llnu(fact, rhs)
#     pmt_trsv_lunn(fact, rhs)
#     return

def pmt_potrsm(fact: pmat, rhs: pmat):
    # solve
    pmt_trsm_llnn(fact, rhs)
    fact_tran = pmat(fact.m, fact.n)
    pmat_tran(fact, fact_tran)
    pmt_trsm_lunn(fact_tran, rhs)
    return

def pmt_potrsv(fact: pmat, rhs: pvec):
    # solve
    pmt_trsv_llnu(fact, rhs)
    pmt_trsv_lunn(fact, rhs)
    return

# intermediate-level linear algebra
def pmt_gemm(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.n != B.m or A.m != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_nn(A, B, C, D)
    return

def pmt_gemm_nn(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.n != B.m or A.m != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_nn: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_nn(A, B, C, D)
    return

def pmt_gemm_nt(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.n != B.n or A.m != C.m or B.m != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_nt: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})^T'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))
    c_pmt_dgemm_nt(A, B, C, D)
    return

def pmt_gemm_tn(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.m != B.m or A.n != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_tn: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {})^T x ({}, {})'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_tn(A, B, C, D)
    return

def pmt_gemm_tt(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.m != B.n or A.n != C.m or B.m != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_tt: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {})^T x ({}, {})^T'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))
    c_pmt_dgemm_tt(A, B, C, D)
    return

# B <= B + alpha*A
def pmt_gead(alpha: float, A: pmat, B: pmat):
    if A.m != B.m or A.n != B.n:
        raise Exception('pmt_dgead: mismatching dimensions:'
            '({},{}) + ({}, {})'.format(A.m, A.n, B.m, B.n))
    c_pmt_dgead(alpha, A, B)
    return

def pmt_rowpe(m: int, ipiv: POINTER(c_int), A: pmat):
    c_pmt_drowpe(m, ipiv, A)
    return

def pmt_trsm_llnu(A: pmat, B: pmat):
    c_pmt_trsm_llnu(A, B)
    return

def pmt_trsm_lunn(A: pmat, B: pmat):
    c_pmt_trsm_lunn(A, B)
    return

def pmt_trsm_llnn(A: pmat, B: pmat):
    c_pmt_trsm_llnn(A, B)
    return

def pmt_trsv_llnu(A: pmat, b: pvec):
    c_pmt_trsv_llnu(A, b)
    return

def pmt_trsv_lunn(A: pmat, b: pvec):
    c_pmt_trsv_lunn(A, b)
    return

def pmt_getrf(A: pmat, fact: pmat, ipiv: list):
    # create permutation vector
    c_ipiv = cast(create_string_buffer(sizeof(c_int)*A.m), POINTER(c_int))
    # factorize
    c_pmt_getrf(A, fact, c_ipiv)
    for i in range(A.n):
        ipiv[i] = c_ipiv[i]
    return

def pmt_potrf(A: pmat, fact: pmat):
    # factorize
    c_pmt_potrf(A, fact)
    return

def pmt_gemv_n(A: pmat, b: pvec, c: pvec, d: pvec):
    c_pmt_dgemv_n(A, b, c, d)
    return

# auxiliary functions
def pmt_set_data(M: pmat, data: POINTER(c_double)):
    c_pmt_set_blasfeo_dmat(M.blasfeo_dmat, data)
    return

def pmat_set(M: pmat, value, i, j):
    c_pmt_set_blasfeo_dmat_el(value, M.blasfeo_dmat, i, j)
    return

def pmat_get(M: pmat, i, j):
    el = c_pmt_get_blasfeo_dmat_el(M.blasfeo_dmat, i, j)
    return el

def pmat_print(M: pmat):
    c_pmt_print_blasfeo_dmat(M)
    return


