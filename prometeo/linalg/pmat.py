from ctypes import *
from .pmat_blasfeo_wrapper import *
from .pvec import *
from .blasfeo_wrapper import *
from multipledispatch import dispatch
from abc import ABC

class pmat_(ABC):
    pass

class pmat(pmat_):
    # sizes in annotations of arguments, A: pmat[n, m], are for the checker
    @classmethod
    def __class_getitem__(cls, sizes):
        return cls

    blasfeo_dmat = None

    def __init__(self, m: int, n: int):
        self.blasfeo_dmat = c_pmt_create_blasfeo_dmat(m, n)
        self._m = m
        self._n = n
        # reference passed to BLASFEO, created once
        self._ref = byref(self.blasfeo_dmat)

    @property
    def m(self):
        return self._m

    @property
    def n(self):
        return self._n

    def __getitem__(self, index):
        # fast path: element A[i, j]
        if type(index) is tuple and len(index) == 2:
            i, j = index
            if type(i) is int and type(j) is int:
                if 0 <= i < self._m and 0 <= j < self._n:
                    return bw.blasfeo_dgeex1(self._ref, i, j)
                raise IndexError('index ({}, {}) out of range for a {}x{} pmat'.format(
                    i, j, self._m, self._n))
        if isinstance(index, tuple):
            if len(index) != 2:
                raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                        you have: {}\n. Exiting'.format(index))
            if isinstance(index[0], int) and isinstance(index[1], int):
                if index[0] < 0 or index[0] >= self.m or \
                        index[1] < 0 or index[1] >= self.n:
                    raise IndexError('index ({}, {}) out of range for a {}x{} pmat'.format(
                        index[0], index[1], self.m, self.n))
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
        # fast path: element A[i, j]
        if type(index) is tuple and len(index) == 2:
            i, j = index
            if type(i) is int and type(j) is int:
                if 0 <= i < self._m and 0 <= j < self._n:
                    bw.blasfeo_dgein1(value, self._ref, i, j)
                    return
                raise IndexError('index ({}, {}) out of range for a {}x{} pmat'.format(
                    i, j, self._m, self._n))
        if isinstance(index, tuple):
            if len(index) != 2:
                raise Exception ('pmat subscript should be a 2-dimensional tuples, \
                        you have: {}\n. Exiting'.format(index))
            if isinstance(index[0], int) and isinstance(index[1], int):
                if index[0] < 0 or index[0] >= self.m or \
                        index[1] < 0 or index[1] >= self.n:
                    raise IndexError('index ({}, {}) out of range for a {}x{} pmat'.format(
                        index[0], index[1], self.m, self.n))
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

    # high-level linear algebra, as in NumPy: these allocate their result.
    # In prometeo programs, matrix expressions are lowered to calls that
    # write into the target matrix (see prometeo/frontend/matexpr.py).
    def __matmul__(self, other):
        if not isinstance(other, pmat_):
            # matrix-vector product
            from .pvec import pvec, pmt_gemv_view_n
            res = pvec(self.m)
            pmt_gemv_view_n(1.0, self, 0, 0, -1, -1, other, 0, -1, 1.0, res, 0, -1, res, 0, -1)
            return res
        res = pmat(self.m, other.n)
        pmt_gemm_ab_nn(1.0, self, other, 1.0, res, res)
        return res

    def __array__(self, dtype=None, copy=None):
        # np.array(A): a copy of the matrix as a NumPy array, e.g. to check,
        # print or plot it in Python-only code (pure blocks)
        import numpy as np
        data = (c_double * (self.m * self.n))()
        bw.blasfeo_unpack_dmat(self.m, self.n, self._ref, 0, 0, data, self.m)
        return np.array(data, dtype=dtype).reshape(self.n, self.m).T.copy()

    @property
    def T(self):
        res = pmat(self.n, self.m)
        pmat_tran(self, res)
        return res

    def __mul__(self, other):
        if isinstance(other, pmat_):
            # elementwise product
            res = pmat(self.m, self.n)
            pmat_mul_view_nn(1.0, self, 0, 0, -1, -1, other, 0, 0, -1, -1, res, 0, 0, -1, -1)
            return res
        res = pmat(self.m, self.n)
        pmat_copy(self, res)
        pmat_scale(float(other), res)
        return res

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * (1.0 / other)

    def __neg__(self):
        return self * -1.0

    def __add__(self, other):
        res = pmat(self.m, self.n)
        pmat_copy(self, res)
        pmt_gead(1.0, other, res)
        return res

    def __sub__(self, other):
        res = pmat(self.m, self.n)
        pmat_copy(self, res)
        pmt_gead(-1.0, other, res)
        return res

def pmat_fill(A: pmat, value: float):
    bw.blasfeo_dgese(A.m, A.n, value, A._ref, 0, 0)
    return

def pmat_copy(A: pmat, B: pmat):
    if A.m != B.m or A.n != B.n:
        raise Exception('__copy__: mismatching dimensions:'
            ' ({}, {}) -> ({}, {})'.format(A.m, A.n, B.m, B.n))
    bw.blasfeo_dgecp(A.m, A.n, A._ref, 0, 0, B._ref, 0, 0)
    return

def pmat_tran(A: pmat, B: pmat):
    if A.m != B.n or A.n != B.m:
        raise Exception('__tran__: mismatching dimensions:'
            ' ({}, {}) -> ({}, {})'.format(A.m, A.n, B.m, B.n))
    bw.blasfeo_dgetr(A.m, A.n, A._ref, 0, 0, B._ref, 0, 0)

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

# rhs <= (fact fact^T)^-1 rhs, fact lower triangular. As in the C runtime
# (the bundled BLASFEO has no dtrsm_lltn), the upper triangle of fact is
# overwritten with the transpose of the lower one.
def pmt_potrsm(fact: pmat, rhs: pmat):
    if fact.m != fact.n or fact.m != rhs.m:
        raise Exception('pmt_potrsm: mismatching dimensions: ({}, {}) \\ ({}, {})'.format(
            fact.m, fact.n, rhs.m, rhs.n))
    bw.blasfeo_dtrsm_llnn(rhs.m, rhs.n, 1.0, fact._ref, 0, 0, rhs._ref, 0, 0, rhs._ref, 0, 0)
    bw.blasfeo_dtrtr_l(fact.m, fact._ref, 0, 0, fact._ref, 0, 0)
    bw.blasfeo_dtrsm_lunn(rhs.m, rhs.n, 1.0, fact._ref, 0, 0, rhs._ref, 0, 0, rhs._ref, 0, 0)
    return

def pmt_potrsv(fact: pmat, rhs: pvec):
    # solve
    pmt_trsv_llnu(fact, rhs)
    pmt_trsv_lunn(fact, rhs)
    return

# intermediate-level linear algebra
# def pmt_gemm(A: pmat, B: pmat, C: pmat, D: pmat):
# D <= beta * C + alpha * A * B, called as pmt_gemm(A, B, D) or pmt_gemm(A, B, C, D)
def pmt_gemm(*argv, alpha=1.0, beta=0.0):
    if len(argv) not in (3, 4):
        raise Exception('Invalid number of arguments')
    A = argv[0]
    B = argv[1]
    C = argv[2]
    D = argv[3] if len(argv) == 4 else argv[2]

    if A.n != B.m or A.m != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm: mismatching dimensions:'
                ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})'.format(\
                    D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_nn(A, B, C, D, alpha, beta)
    return

def pmt_gemm_nn(*argv):
    if len(argv) < 3:
        raise Exception('Invalid number of arguments')
    A = argv[0]
    B = argv[1]
    if len(argv) == 4:
        C = argv[2]
        D = argv[3]
    else:
        C = argv[2]
        D = argv[2]
    if A.n != B.m or A.m != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_nn: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_nn(A, B, C, D)
    return

def pmt_gemm_nt(*argv):
    if len(argv) < 3:
        raise Exception('Invalid number of arguments')
    A = argv[0]
    B = argv[1]
    if len(argv) == 4:
        C = argv[2]
        D = argv[3]
    else:
        C = argv[2]
        D = argv[2]
    if A.n != B.n or A.m != C.m or B.m != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_nt: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {}) x ({}, {})^T'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))
    c_pmt_dgemm_nt(A, B, C, D)
    return

def pmt_gemm_tn(*argv):
    if len(argv) < 3:
        raise Exception('Invalid number of arguments')
    A = argv[0]
    B = argv[1]
    if len(argv) == 4:
        C = argv[2]
        D = argv[3]
    else:
        C = argv[2]
        D = argv[2]
    if A.m != B.m or A.n != C.m or B.n != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_tn: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {})^T x ({}, {})'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))

    c_pmt_dgemm_tn(A, B, C, D)
    return

def pmt_gemm_tt(*argv):
    if len(argv) < 3:
        raise Exception('Invalid number of arguments')
    A = argv[0]
    B = argv[1]
    if len(argv) == 4:
        C = argv[2]
        D = argv[3]
    else:
        C = argv[2]
        D = argv[2]
    if A.m != B.n or A.n != C.m or B.m != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_gemm_tt: mismatching dimensions:'
            ' ({}, {}) <- ({},{}) + ({}, {})^T x ({}, {})^T'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))
    c_pmt_dgemm_tt(A, B, C, D)
    return

# D <= B * A, with A lower triangular
def pmt_trmm_rlnn(A: pmat, B: pmat, D: pmat):
    if A.m != A.n or B.n != A.m or B.m != D.m or B.n != D.n:
        raise Exception('pmt_trmm_rlnn: mismatching dimensions:'
            ' ({}, {}) <- ({}, {}) x ({}, {})'.format(\
            D.m, D.n, B.m, B.n, A.m, A.n))
    c_pmt_dtrmm_rlnn(A, B, D)
    return

# D <= C + A * B^T (lower triangular part only)
def pmt_syrk_ln(A: pmat, B: pmat, C: pmat, D: pmat):
    if A.n != B.n or A.m != B.m or A.m != C.m or C.m != C.n or C.m != D.m or C.n != D.n:
        raise Exception('pmt_syrk_ln: mismatching dimensions:'
            ' ({}, {}) <- ({}, {}) + ({}, {}) x ({}, {})^T'.format(\
            D.m, D.n, C.m, C.n, A.m, A.n, B.m, B.n))
    c_pmt_dsyrk_ln(A, B, C, D)
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
    if A.m != A.n or fact.m != A.m or fact.n != A.n:
        raise Exception('pmt_potrf: mismatching dimensions: ({}, {}) -> ({}, {})'.format(
            A.m, A.n, fact.m, fact.n))
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



def _check_gemm(name, ta, tb, A, B, C, D):
    m, k = (A.n, A.m) if ta else (A.m, A.n)
    kb, n = (B.n, B.m) if tb else (B.m, B.n)
    if k != kb or C.m != m or C.n != n or D.m != m or D.n != n:
        raise Exception('{}: mismatching dimensions: ({}, {}) <- ({}, {}) + ({}, {}){} x ({}, {}){}'.format(
            name, D.m, D.n, C.m, C.n, A.m, A.n, '^T' if ta else '', B.m, B.n, '^T' if tb else ''))
    return m, n, k

# D <= beta * C + alpha * op(A) op(B), op(X) = X (n) or X^T (t)
def pmt_gemm_ab_nn(alpha: float, A: pmat, B: pmat, beta: float, C: pmat, D: pmat):
    m, n, k = _check_gemm('pmt_gemm_ab_nn', False, False, A, B, C, D)
    bw.blasfeo_dgemm_nn(m, n, k, alpha, A._ref, 0, 0, B._ref, 0, 0, beta, C._ref, 0, 0, D._ref, 0, 0)

def pmt_gemm_ab_nt(alpha: float, A: pmat, B: pmat, beta: float, C: pmat, D: pmat):
    m, n, k = _check_gemm('pmt_gemm_ab_nt', False, True, A, B, C, D)
    bw.blasfeo_dgemm_nt(m, n, k, alpha, A._ref, 0, 0, B._ref, 0, 0, beta, C._ref, 0, 0, D._ref, 0, 0)

def pmt_gemm_ab_tn(alpha: float, A: pmat, B: pmat, beta: float, C: pmat, D: pmat):
    m, n, k = _check_gemm('pmt_gemm_ab_tn', True, False, A, B, C, D)
    bw.blasfeo_dgemm_tn(m, n, k, alpha, A._ref, 0, 0, B._ref, 0, 0, beta, C._ref, 0, 0, D._ref, 0, 0)

def pmt_gemm_ab_tt(alpha: float, A: pmat, B: pmat, beta: float, C: pmat, D: pmat):
    m, n, k = _check_gemm('pmt_gemm_ab_tt', True, True, A, B, C, D)
    bw.blasfeo_dgemm_tt(m, n, k, alpha, A._ref, 0, 0, B._ref, 0, 0, beta, C._ref, 0, 0, D._ref, 0, 0)

# A <= alpha * A
def pmat_scale(alpha: float, A: pmat):
    bw.blasfeo_dgesc(A.m, A.n, alpha, A._ref, 0, 0)

# L L^T = A, L lower triangular (as numpy.linalg.cholesky)
def cholesky(A: pmat):
    if A.m != A.n:
        raise Exception('cholesky: the matrix must be square, not ({}, {})'.format(A.m, A.n))
    L = pmat(A.m, A.n)
    pmt_potrf(A, L)
    return L

# X = (L L^T)^-1 B, with L from cholesky (as scipy.linalg.cho_solve)
def cho_solve(L: pmat, B: pmat):
    if not isinstance(B, pmat_):
        from .pvec import cho_solve_vec
        return cho_solve_vec(L, B)
    X = pmat(B.m, B.n)
    pmat_copy(B, X)
    fact = pmat(L.m, L.n)
    pmat_copy(L, fact)
    pmt_potrsm(fact, X)
    return X


# Blocks of matrices, used by matrix expressions with blocks A[a:b, c:d]: a
# block is passed as A, a, c, b - a, d - c, a whole matrix as A, 0, 0, -1, -1.
def _view(name, M, i, j, r, c):
    if r < 0:
        r = M.m - i
    if c < 0:
        c = M.n - j
    if i < 0 or j < 0 or r <= 0 or c <= 0 or i + r > M.m or j + c > M.n:
        raise IndexError('{}: block [{}:{}, {}:{}] out of range for a {}x{} pmat'.format(
            name, i, i + r, j, j + c, M.m, M.n))
    return i, j, r, c

def _same_size(name, *sizes):
    if len(set(sizes[0::2])) != 1 or len(set(sizes[1::2])) != 1:
        raise Exception('{}: mismatching dimensions: {}'.format(name, ', '.join(
            '({}, {})'.format(m, n) for m, n in zip(sizes[0::2], sizes[1::2]))))

def pmat_copy_view(A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int):
    ai, aj, ar, ac = _view('pmat_copy', A, ai, aj, ar, ac)
    bi, bj, br, bc = _view('pmat_copy', B, bi, bj, br, bc)
    _same_size('pmat_copy', ar, ac, br, bc)
    bw.blasfeo_dgecp(ar, ac, A._ref, ai, aj, B._ref, bi, bj)

def pmat_tran_view(A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int):
    ai, aj, ar, ac = _view('pmat_tran', A, ai, aj, ar, ac)
    bi, bj, br, bc = _view('pmat_tran', B, bi, bj, br, bc)
    _same_size('pmat_tran', ac, ar, br, bc)
    bw.blasfeo_dgetr(ar, ac, A._ref, ai, aj, B._ref, bi, bj)

def pmat_fill_view(value: float, A: pmat, ai: int, aj: int, ar: int, ac: int):
    ai, aj, ar, ac = _view('pmat_fill', A, ai, aj, ar, ac)
    bw.blasfeo_dgese(ar, ac, value, A._ref, ai, aj)

def pmat_scale_view(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int):
    ai, aj, ar, ac = _view('pmat_scale', A, ai, aj, ar, ac)
    bw.blasfeo_dgesc(ar, ac, alpha, A._ref, ai, aj)

def pmt_gead_view(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int):
    ai, aj, ar, ac = _view('pmt_gead', A, ai, aj, ar, ac)
    bi, bj, br, bc = _view('pmt_gead', B, bi, bj, br, bc)
    _same_size('pmt_gead', ar, ac, br, bc)
    bw.blasfeo_dgead(ar, ac, alpha, A._ref, ai, aj, B._ref, bi, bj)

def _gemm_view(t, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, beta, C, ci, cj, cr, cc,
        D, di, dj, dr, dc):
    name = 'pmt_gemm_' + t
    ai, aj, ar, ac = _view(name, A, ai, aj, ar, ac)
    bi, bj, br, bc = _view(name, B, bi, bj, br, bc)
    ci, cj, cr, cc = _view(name, C, ci, cj, cr, cc)
    di, dj, dr, dc = _view(name, D, di, dj, dr, dc)
    m, k = (ac, ar) if t[0] == 't' else (ar, ac)
    kb, n = (bc, br) if t[1] == 't' else (br, bc)
    _same_size(name, m, n, cr, cc, dr, dc)
    if k != kb:
        raise Exception('{}: mismatching dimensions: ({}, {}){} x ({}, {}){}'.format(
            name, ar, ac, '^T' if t[0] == 't' else '', br, bc, '^T' if t[1] == 't' else ''))
    getattr(bw, 'blasfeo_dgemm_' + t)(m, n, k, alpha, A._ref, ai, aj, B._ref, bi, bj,
        beta, C._ref, ci, cj, D._ref, di, dj)

def pmt_gemm_view_nn(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, beta: float,
        C: pmat, ci: int, cj: int, cr: int, cc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _gemm_view('nn', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, beta, C, ci, cj, cr, cc,
        D, di, dj, dr, dc)

def pmt_gemm_view_nt(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, beta: float,
        C: pmat, ci: int, cj: int, cr: int, cc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _gemm_view('nt', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, beta, C, ci, cj, cr, cc,
        D, di, dj, dr, dc)

def pmt_gemm_view_tn(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, beta: float,
        C: pmat, ci: int, cj: int, cr: int, cc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _gemm_view('tn', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, beta, C, ci, cj, cr, cc,
        D, di, dj, dr, dc)

def pmt_gemm_view_tt(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, beta: float,
        C: pmat, ci: int, cj: int, cr: int, cc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _gemm_view('tt', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, beta, C, ci, cj, cr, cc,
        D, di, dj, dr, dc)


# D <= D + alpha * op(A) .* op(B), elementwise (the same operations, in the
# same order, as c_pmt_pmat_mul_view in the C runtime)
def _mul_view(t, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc):
    name = 'pmat_mul'
    ai, aj, ar, ac = _view(name, A, ai, aj, ar, ac)
    bi, bj, br, bc = _view(name, B, bi, bj, br, bc)
    di, dj, dr, dc = _view(name, D, di, dj, dr, dc)
    sa = (ac, ar) if t[0] == 't' else (ar, ac)
    sb = (bc, br) if t[1] == 't' else (br, bc)
    _same_size(name, sa[0], sa[1], sb[0], sb[1], dr, dc)
    get, put = bw.blasfeo_dgeex1, bw.blasfeo_dgein1
    for j in range(dc):
        for i in range(dr):
            a = get(A._ref, ai + j, aj + i) if t[0] == 't' else get(A._ref, ai + i, aj + j)
            b = get(B._ref, bi + j, bj + i) if t[1] == 't' else get(B._ref, bi + i, bj + j)
            put(get(D._ref, di + i, dj + j) + alpha * (a * b), D._ref, di + i, dj + j)

def pmat_mul_view_nn(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _mul_view('nn', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc)

def pmat_mul_view_nt(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _mul_view('nt', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc)

def pmat_mul_view_tn(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _mul_view('tn', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc)

def pmat_mul_view_tt(alpha: float, A: pmat, ai: int, aj: int, ar: int, ac: int,
        B: pmat, bi: int, bj: int, br: int, bc: int, D: pmat, di: int, dj: int, dr: int, dc: int):
    _mul_view('tt', alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc)
