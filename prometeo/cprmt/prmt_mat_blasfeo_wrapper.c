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

// BLAS API

void ___c_prmt___dgemm(struct prmt_mat *A, struct prmt_mat *B, struct prmt_mat *C, struct prmt_mat *D) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    int nB = B->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    struct blasfeo_dmat *bC = C->bmat;
    struct blasfeo_dmat *bD = D->bmat;

    blasfeo_dgemm_nn(mA, nA, nB, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}

void ___c_prmt___dgead(double alpha, struct prmt_mat *A, struct prmt_mat *B) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;

    blasfeo_dgead(mA, nA, alpha, bA, 0, 0, bB, 0, 0);
}

// auxiliary
void ___c_prmt___fill(struct prmt_mat *A, double fill_value) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    for(int i = 0; i < m; i++)
        for(int j = 0; j < n; j++)
            blasfeo_dgein1(fill_value, A->bmat, i, j);
}

void ___c_prmt___copy(struct prmt_mat *A, struct prmt_mat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    double value;

    for(int i = 0; i < m; i++)
        for(int j = 0; j < n; j++) {
            value = blasfeo_dgeex1(A->bmat, i, j);
            blasfeo_dgein1(value, B->bmat, i, j);
        }
}

void ___c_prmt___print(struct prmt_mat *A) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    blasfeo_print_dmat(m, n, A->bmat, 0, 0);
}
