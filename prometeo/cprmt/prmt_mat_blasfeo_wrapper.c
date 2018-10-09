#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include <blasfeo_common.h>

struct prmt_mat * ___c_prmt___create_prmt_mat(int m, int n){	
    // assign current address of global heap to pmat pointer
    struct prmt_mat *pmat = (struct prmt_mat *) ___c_prmt_heap;
    void *pmat_address = ___c_prmt_heap;
    // advance global heap address
    ___c_prmt_heap += sizeof(struct prmt_mat);
    
    
    // create (zeroed) blasfeo_dmat and advance global heap
    ___c_prmt___assign_and_advance_blasfeo_dmat(m, n, &(pmat->bmat));

	return (struct prmt_mat *)(pmat_address);
}

void ___c_prmt___assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat) {
    // assign current address of global heap to blasfeo dmat pointer
    *bmat = (struct blasfeo_dmat *) ___c_prmt_heap;
    // advance global heap address
    ___c_prmt_heap += sizeof(struct blasfeo_dmat);

    // assign current address of global heap to memory in blasfeo dmat
    blasfeo_create_dmat(m, n, *bmat, ___c_prmt_heap);
    // advance global heap address
    ___c_prmt_heap += (*bmat)->memsize;
	// zero allocated memory
	int i;
	double *dA = (*bmat)->dA;
    int size = (*bmat)->memsize;
	for(i=0; i<size/8; i++) dA[i] = 0.0;
	char *cA = (char *) dA;
	i *= 8;
	for(; i<size; i++) cA[i] = 0;
	return;
}
