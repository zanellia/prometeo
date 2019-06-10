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

struct pmat * ___c_prmt___create_pmat(int m, int n);	
void ___c_prmt___assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat);

// BLAS API
void ___c_prmt___dgemm(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D);
void ___c_prmt___dgead(double alpha, struct pmat *A, struct pmat *B); 

void ___c_prmt___dgemv(struct pmat *A, struct pvec *b, struct pvec *c, struct pvec *d);

// auxiliary
void ___c_prmt___fill(struct pmat *A, double fill_value);
void ___c_prmt___prmt_set_el(struct pmat *A, int i, int j, double value);
double ___c_prmt___prmt_get_el(struct pmat *A, int i, int j);
void ___c_prmt___copy(struct pmat *A, struct pmat *B);
void ___c_prmt___print(struct pmat *A);

#endif // PROMETEO_PRMT_MAT_BLASFEO_WRAPPER_H_

