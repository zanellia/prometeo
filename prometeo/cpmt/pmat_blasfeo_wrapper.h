#ifndef PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_
#define PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

#include <blasfeo_common.h>
#include <blasfeo_i_aux_ext_dep.h>
#include <blasfeo_v_aux_ext_dep.h>
#include <blasfeo_d_aux_ext_dep.h>
#include <blasfeo_d_aux.h>
#include <blasfeo_d_kernel.h>
#include <blasfeo_d_blas.h>
#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"

#ifdef __cplusplus
extern "C" {
#endif

// (dummy) pmat wrapper to blasfeo_dmat
struct pmat {
    struct blasfeo_dmat *bmat;
};

struct pmat * c_pmt_create_pmat(int m, int n);	
void c_pmt_assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat);

// BLAS API
void c_pmt_gemm_nn(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void c_pmt_gemm_ab(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D);
// D <= beta * C + alpha * op(A) op(B), op(X) = X (n) or X^T (t)
void c_pmt_gemm_ab_nn(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D);
void c_pmt_gemm_ab_nt(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D);
void c_pmt_gemm_ab_tn(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D);
void c_pmt_gemm_ab_tt(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D);
struct pmat * _c_pmt_gemm_nn(struct pmat *A, struct pmat *B);
void c_pmt_gemm_tn(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void c_pmt_gemm_nt(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void c_pmt_trmm_rlnn(struct pmat *A, struct pmat *B, struct pmat *D);
void c_pmt_syrk_ln(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void c_pmt_getrf(struct pmat *A, struct pmat *fact, int *ipiv);
void c_pmt_potrf(struct pmat *A, struct pmat *fact);
void c_pmt_getrsm(struct pmat *fact, int *ipiv, struct pmat *rhs);
struct pmat * _c_pmt_getrsm(struct pmat *A, struct pmat *rhs);
void c_pmt_getrsv(struct pmat *fact, int *ipiv, struct pvec *rhs);
void c_pmt_potrsm(struct pmat *fact, struct pmat *rhs);
void c_pmt_potrsv(struct pmat *fact, struct pvec *rhs);
void c_pmt_gead(double alpha, struct pmat *A, struct pmat *B); 
struct pmat * _c_pmt_gead(double alpha, struct pmat *A, struct pmat *B); 

void c_pmt_gemv_n(struct pmat *A, struct pvec *b, struct pvec *c, struct pvec *d);

// blocks of matrices (matrix expressions with A[a:b, c:d]): a matrix
// argument is (M, first row, first column, rows, columns), with -1 rows or
// columns for all of them
void c_pmt_pmat_copy_view(struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc);
void c_pmt_pmat_tran_view(struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc);
void c_pmt_pmat_fill_view(double value, struct pmat *A, int ai, int aj, int ar, int ac);
void c_pmt_pmat_scale_view(double alpha, struct pmat *A, int ai, int aj, int ar, int ac);
void c_pmt_gead_view(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc);
void c_pmt_gemm_view_nn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc);
void c_pmt_gemm_view_nt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc);
void c_pmt_gemm_view_tn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc);
void c_pmt_gemm_view_tt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc);

// vectors and slices of vectors (vector expressions with v[a:b]): a vector
// argument is (v, first element, size), with -1 for all the elements
void c_pmt_pvec_copy_view(struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr);
void c_pmt_pvec_fill_view(double value, struct pvec *x, int xi, int xr);
void c_pmt_pvec_scale_view(double alpha, struct pvec *x, int xi, int xr);
void c_pmt_pvec_axpy_view(double alpha, struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr);
double c_pmt_pvec_dot_view(struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr);
void c_pmt_gemv_view_n(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pvec *x, int xi, int xr, double beta, struct pvec *y, int yi, int yr, struct pvec *z, int zi, int zr);
void c_pmt_gemv_view_t(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pvec *x, int xi, int xr, double beta, struct pvec *y, int yi, int yr, struct pvec *z, int zi, int zr);
void c_pmt_potrsv_view(struct pmat *L, struct pvec *x, int xi, int xr);


// auxiliary
void c_pmt_pmat_fill(struct pmat *A, double fill_value);
// A <= alpha * A
void c_pmt_pmat_scale(double alpha, struct pmat *A);
// element access, inlined (as blasfeo_dgein1 and blasfeo_dgeex1)
static inline void c_pmt_pmat_set_el(struct pmat *A, int i, int j, double value) {
    if (i == j) {
        // invalidate the stored inverse diagonal
        A->bmat->use_dA = 0;
    }
    BLASFEO_DMATEL(A->bmat, i, j) = value;
}

static inline double c_pmt_pmat_get_el(struct pmat *A, int i, int j) {
    return BLASFEO_DMATEL(A->bmat, i, j);
}
void c_pmt_pmat_copy(struct pmat *A, struct pmat *B);
struct pmat * _c_pmt_pmat_copy(struct pmat *A, struct pmat *B);
void c_pmt_pmat_tran(struct pmat *A, struct pmat *B);
struct pmat * _c_pmt_pmat_tran(struct pmat *A);
void c_pmt_gecp(int m, int n, struct pmat *A, int ai, int aj, struct pmat *B, int bi, int bj);
void c_pmt_pmat_vcat(struct pmat *A, struct pmat *B, struct pmat *res);
void c_pmt_pmat_hcat(struct pmat *A, struct pmat *B, struct pmat *res);
void c_pmt_pmat_print(struct pmat *A);

#ifdef __cplusplus
}
#endif

#endif // PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

