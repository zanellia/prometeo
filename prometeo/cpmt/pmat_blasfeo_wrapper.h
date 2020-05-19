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

// auxiliary
void c_pmt_pmat_fill(struct pmat *A, double fill_value);
void c_pmt_pmat_set_el(struct pmat *A, int i, int j, double value);
double c_pmt_pmat_get_el(struct pmat *A, int i, int j);
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

