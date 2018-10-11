#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include <assert.h>
#include <blasfeo_common.h>

void make_int_multiple_of(int num, int *size) { *size = (*size + num - 1) / num * num; }

int align_char_to(int num, char **c_ptr)
{
    size_t s_ptr = (size_t) *c_ptr;
    s_ptr = (s_ptr + num - 1) / num * num;
    int offset = num - (int) (s_ptr - (size_t)(*c_ptr));
    *c_ptr = (char *) s_ptr;
    return offset;
}

struct prmt_mat * ___c_prmt___create_prmt_mat(int m, int n) {	
    // assign current address of global heap to pmat pointer
    struct prmt_mat *pmat = (struct prmt_mat *) ___c_prmt_8_heap;
    void *pmat_address = ___c_prmt_8_heap;
    
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct prmt_mat);
    
    
    // create (zeroed) blasfeo_dmat and advance global heap
    ___c_prmt___assign_and_advance_blasfeo_dmat(m, n, &(pmat->bmat));

	return (struct prmt_mat *)(pmat_address);
}

void ___c_prmt___assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat) {
    // assign current address of global heap to blasfeo dmat pointer
    assert((size_t) ___c_prmt_8_heap % 8 == 0 && "pointer not 8-byte aligned!");
    *bmat = (struct blasfeo_dmat *) ___c_prmt_8_heap;
    //
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct blasfeo_dmat);

    // assign current address of global heap to memory in blasfeo dmat
    char *mem_ptr = (char *)___c_prmt_64_heap;
    // align_char_to(64, &mem_ptr);
    // ___c_prmt_heap = mem_ptr;
    assert((size_t) ___c_prmt_64_heap % 64 == 0 && "dmat not 64-byte aligned!");
    blasfeo_create_dmat(m, n, *bmat, ___c_prmt_64_heap);

    // advance global heap address
    int memsize = (*bmat)->memsize;
    // make_int_multiple_of(64, memsize);
    ___c_prmt_64_heap += memsize;	

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

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

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
