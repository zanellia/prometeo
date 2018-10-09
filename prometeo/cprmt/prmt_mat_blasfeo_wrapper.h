#include "blasfeo_common.h"
#include "blasfeo_i_aux_ext_dep.h"
#include "blasfeo_v_aux_ext_dep.h"
#include "blasfeo_d_aux_ext_dep.h"
#include "blasfeo_d_aux.h"
#include "blasfeo_d_kernel.h"
#include "blasfeo_d_blas.h"

// (dummy) prmt_mat wrapper to blasfeo_dmat
struct prmt_mat {
    blasfeo_dmat * bmat;
}


void ___c_prmt___create_prmt_mat(int m, int n);	
void __c_prmt_assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat);
