#ifndef PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_
#define PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

#include <blasfeo_common.h>
#include <blasfeo_i_aux_ext_dep.h>
#include <blasfeo_v_aux_ext_dep.h>
#include <blasfeo_d_aux_ext_dep.h>
#include <blasfeo_d_aux.h>
#include <blasfeo_d_kernel.h>
#include <blasfeo_d_blas.h>

// (dummy) prmt_mat wrapper to blasfeo_dmat
struct prmt_mat {
    struct blasfeo_dmat *bmat;
};

struct prmt_mat * ___c_prmt___create_prmt_mat(int m, int n);	
void ___c_prmt___assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat);

// BLAS API
void ___c_pmrt___dgemm(struct prmt_mat *A, struct prmt_mat *B, struct prmt_mat *C, struct prmt_mat *D);
void ___c_pmrt___dgead(double alpha, struct prmt_mat *A, struct prmt_mat *B); 

// auxiliary
void ___c_pmrt___prmt_fill(struct prmt_mat *A, double fill_value);
void ___c_pmrt___prmt_print(struct prmt_mat *A);
void ___c_pmrt___prmt_copy(struct prmt_mat *A, struct prmt_mat *B, double fill_value);

#endif // PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

