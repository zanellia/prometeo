"""Signatures of the built-in functions accepted by the checker.

Only functions that are supported both when running in Python and in
transpiled C code are listed here.
"""

from .types import FLOAT, NONE, PMAT, PVEC, INT, list_of

# name -> list of accepted signatures (argument types, return type)
BUILTINS = {
    'pmat_print': [((PMAT,), NONE)],
    'pvec_print': [((PVEC,), NONE)],
    'pmat_fill': [((PMAT, FLOAT), NONE)],
    'pmat_copy': [((PMAT, PMAT), NONE)],
    'pvec_copy': [((PVEC, PVEC), NONE)],
    'pmat_tran': [((PMAT, PMAT), NONE)],
    'pmat_hcat': [((PMAT, PMAT, PMAT), NONE)],
    'pmt_gemm': [((PMAT, PMAT, PMAT), NONE), ((PMAT, PMAT, PMAT, PMAT), NONE)],
    'pmt_gemm_nn': [((PMAT, PMAT, PMAT, PMAT), NONE)],
    'pmt_gemm_nt': [((PMAT, PMAT, PMAT, PMAT), NONE)],
    'pmt_gemm_tn': [((PMAT, PMAT, PMAT, PMAT), NONE)],
    'pmt_gead': [((FLOAT, PMAT, PMAT), NONE)],
    'pmt_potrf': [((PMAT, PMAT), NONE)],
    'pmt_potrsm': [((PMAT, PMAT), NONE)],
    'pmt_trmm_rlnn': [((PMAT, PMAT, PMAT), NONE)],
    'pmt_syrk_ln': [((PMAT, PMAT, PMAT, PMAT), NONE)],
    'pmt_getrf': [((PMAT, PMAT, list_of(INT)), NONE)],
}

# keyword arguments accepted by built-in functions (float literals)
BUILTIN_KEYWORDS = {
    'pmt_gemm': {'alpha', 'beta'},
}

# functions that exist in Python but cannot be transpiled (yet)
UNSUPPORTED_BUILTINS = {
    'pmat_vcat', 'pmt_gemm_tt', 'pmt_gemv_n', 'pmt_potrsv', 'pmt_getrsm',
    'pmt_getrsv', 'pmt_trsm_llnu', 'pmt_trsm_lunn', 'pmt_trsm_llnn',
    'pmt_trsv_llnu', 'pmt_trsv_lunn', 'pmt_rowpe', 'pmt_set_data',
    'pmat_set', 'pmat_get', 'pfun', 'pparse',
}

# name -> (index of the output argument, indices of the arguments it must not
# alias): computing these in place gives wrong (and mode-dependent) results.
# Unlisted aliasing is fine, e.g. pmt_gemm_nn(A, B, C, C) or pmt_potrf(M, M).
OUTPUT_ALIASING = {
    'pmat_tran': (1, (0,)),
    'pmat_hcat': (2, (0, 1)),
    'pmt_gemm': (-1, (0, 1)),
    'pmt_gemm_nn': (-1, (0, 1)),
    'pmt_gemm_nt': (-1, (0, 1)),
    'pmt_gemm_tn': (-1, (0, 1)),
    'pmt_potrsm': (1, (0,)),
    'pmt_trmm_rlnn': (2, (0, 1)),
    'pmt_syrk_ln': (3, (0, 1)),
}
