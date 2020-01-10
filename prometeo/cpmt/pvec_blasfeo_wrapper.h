#ifndef PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_
#define PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

#include <blasfeo_common.h>
#include <blasfeo_i_aux_ext_dep.h>
#include <blasfeo_v_aux_ext_dep.h>
#include <blasfeo_d_aux_ext_dep.h>
#include <blasfeo_d_aux.h>
#include <blasfeo_d_kernel.h>
#include <blasfeo_d_blas.h>

#ifdef __cplusplus
extern "C" {
#endif

// (dummy) pvec wrapper to blasfeo_dvec
struct pvec {
    struct blasfeo_dvec *bvec;
};

struct pvec * c_pmt_create_pvec(int m);	
void c_pmt_assign_and_advance_blasfeo_dvec(int m, struct blasfeo_dvec **bvec);

// BLAS API
// void c_pmt_dgemm(struct pvec *A, struct pvec *B, struct pvec *C, struct pvec *D);
// void c_pmt_dgead(double alpha, struct pvec *A, struct pvec *B); 

// auxiliary
void c_pmt_pvec_fill(struct pvec *a, double fill_value);
void c_pmt_pvec_set_el(struct pvec *a, int i, double value);
double c_pmt_pvec_get_el(struct pvec *a, int i);
void c_pmt_pvec_copy(struct pvec *a, struct pvec *b);
void c_pmt_pvec_print(struct pvec *a);

#ifdef __cplusplus
}
#endif

#endif // PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

