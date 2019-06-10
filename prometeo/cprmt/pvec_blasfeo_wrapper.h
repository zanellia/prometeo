#ifndef PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_
#define PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

#include <blasfeo_common.h>
#include <blasfeo_i_aux_ext_dep.h>
#include <blasfeo_v_aux_ext_dep.h>
#include <blasfeo_d_aux_ext_dep.h>
#include <blasfeo_d_aux.h>
#include <blasfeo_d_kernel.h>
#include <blasfeo_d_blas.h>

// (dummy) pvec wrapper to blasfeo_dvec
struct pvec {
    struct blasfeo_dvec *bvec;
};

struct pvec * ___c_prmt___create_pvec(int m);	
void ___c_prmt___assign_and_advance_blasfeo_dvec(int m, struct blasfeo_dvec **bvec);

// BLAS API
// void ___c_prmt___dgemm(struct pvec *A, struct pvec *B, struct pvec *C, struct pvec *D);
// void ___c_prmt___dgead(double alpha, struct pvec *A, struct pvec *B); 

// auxiliary
void ___c_prmt___fill_vec(struct pvec *a, double fill_value);
void ___c_prmt___prmt_set_el_vec(struct pvec *a, int i, double value);
double ___c_prmt___prmt_get_el_vec(struct pvec *a, int i);
void ___c_prmt___copy_vec(struct pvec *a, struct pvec *b);
void ___c_prmt___print_vec(struct pvec *a);

#endif // PROMETEO_PRMT_VEC_BLASFEO_WRAPPER_H_

