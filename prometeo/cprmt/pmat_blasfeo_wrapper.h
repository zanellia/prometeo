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

// (dummy) pmat wrapper to blasfeo_dmat
struct pmat {
    struct blasfeo_dmat *bmat;
};

struct pmat * c_pmt_create_pmat(int m, int n);	
void c_pmt_assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat);

// BLAS API
void c_pmt_dgemm(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void c_pmt_dgead(double alpha, struct pmat *A, struct pmat *B); 

void c_pmt_dgemv(struct pmat *A, struct pvec *b, struct pvec *c, struct pvec *d);

// auxiliary
void c_pmt_pmat_fill(struct pmat *A, double fill_value);
void c_pmt_pmat_set_el(struct pmat *A, int i, int j, double value);
double c_pmt_pmat_get_el(struct pmat *A, int i, int j);
void c_pmt_pmat_copy(struct pmat *A, struct pmat *B);
void c_pmt_pmat_print(struct pmat *A);

#endif // PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

