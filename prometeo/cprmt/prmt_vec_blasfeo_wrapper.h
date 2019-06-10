#ifndef PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_
#define PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

#include <blasfeo_common.h>
#include <blasfeo_i_aux_ext_dep.h>
#include <blasfeo_v_aux_ext_dep.h>
#include <blasfeo_d_aux_ext_dep.h>
#include <blasfeo_d_aux.h>
#include <blasfeo_d_kernel.h>
#include <blasfeo_d_blas.h>

// (dummy) prmt_vec wrapper to blasfeo_dvec
struct prmt_vec {
    struct blasfeo_dvec *bvec;
};

struct prmt_vec * ___c_prmt___create_prmt_vec(int m);	
void ___c_prmt___assign_and_advance_blasfeo_dvec(int m, struct blasfeo_dvec **bvec);

// BLAS API
// void ___c_prmt___dgemm(struct prmt_vec *A, struct prmt_vec *B, struct prmt_vec *C, struct prmt_vec *D);
// void ___c_prmt___dgead(double alpha, struct prmt_vec *A, struct prmt_vec *B); 

// auxiliary
void ___c_prmt___fill_vec(struct prmt_vec *a, double fill_value);
void ___c_prmt___prmt_set_el_vec(struct prmt_vec *a, int i, double value);
double ___c_prmt___prmt_get_el_vec(struct prmt_vec *a, int i);
void ___c_prmt___copy_vec(struct prmt_vec *a, struct prmt_vec *b);
void ___c_prmt___print_vec(struct prmt_vec *a);

#endif // PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

