#include "include/blasfeo_common.h"
#include "include/blasfeo_i_aux_ext_dep.h"
#include "include/blasfeo_v_aux_ext_dep.h"
#include "include/blasfeo_d_aux_ext_dep.h"
#include "include/blasfeo_d_aux.h"
#include "include/blasfeo_d_kernel.h"
#include "include/blasfeo_d_blas.h"


void ___c_prmt___create_prmt_mat(int m, int n, double* data){	
	int size_strmat = blasfeo_memsize_dmat(m, n);
	void *memory_strmat; 
	v_zeros_align(&memory_strmat, size_strmat);
	char *ptr_memory_strmat = (char *) memory_strmat;

	struct blasfeo_dmat sA;
 	//	blasfeo_allocate_dmat(n, n, &sA);
	blasfeo_create_dmat(m, n, &sA, ptr_memory_strmat);
	ptr_memory_strmat += sA.memsize;
	// convert from column major matrix to strmat
	blasfeo_pack_dmat(m, n, A, m, &data, 0, 0);
	return;
}

void ___c_prmt___dgemm_nt(blasfeo_dmat *A, blasfeo_dmat *B, blasfeo_dmat *C){
	blasfeo_dgemm_nt(A->m, A->n, B->n, 1.0, A, 0, 0, B, 0, 0, 1.0, C, 0, 0, C, 0, 0);
}
