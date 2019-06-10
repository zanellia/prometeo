#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
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

struct pmat * ___c_prmt___create_pmat(int m, int n) {	
    // assign current address of global heap to pmat pointer
    struct pmat *pmat = (struct pmat *) ___c_prmt_8_heap;
    void *pmat_address = ___c_prmt_8_heap;
    
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct pmat);
    
    
    // create (zeroed) blasfeo_dmat and advance global heap
    ___c_prmt___assign_and_advance_blasfeo_dmat(m, n, &(pmat->bmat));

	return (struct pmat *)(pmat_address);
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

void ___c_prmt___dgemm(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
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

// void ___c_prmt___lus(struct pmat *A, struct pmat *B, struct pmat *C) {
//     int mA = A->bmat->m; 
//     int nA = A->bmat->n; 
//     int nB = B->bmat->n; 
//     struct blasfeo_dmat *bA = A->bmat;
//     struct blasfeo_dmat *bB = B->bmat;
//     struct blasfeo_dmat *bC = C->bmat;

//     // printf("In dgemm\n");
//     // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
//     // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
//     // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
//     // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

//     // allocate memory for pivots
//     // factorization
//     blasfeo_dgetrf_rp(m, n, dG_dK_ss, 0, 0, dG_dK_ss, 0, 0, ipiv);
//     // permute the r.h.s
//     blasfeo_dvecpe(nK, ipiv_ss, rG, 0);
//     // triangular solves 
//     blasfeo_dtrsv_lnu(nK, dG_dK_ss, 0, 0, rG, 0, rG, 0);
//     blasfeo_dtrsv_unn(nK, dG_dK_ss, 0, 0, rG, 0, rG, 0);
// }

void ___c_prmt___dgead(double alpha, struct pmat *A, struct pmat *B) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;

    blasfeo_dgead(mA, nA, alpha, bA, 0, 0, bB, 0, 0);
}

void ___c_prmt___dgemv(struct pmat *A, struct pvec *b, struct pvec *c, struct pvec *d) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    int mb = b->bvec->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dvec *bb = b->bvec;
    struct blasfeo_dvec *bc = c->bvec;
    struct blasfeo_dvec *bd = d->bvec;

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

    blasfeo_dgemv_n(mA, nA, 1.0, bA, 0, 0, bb, 0, 1.0, bc,
           0, bd, 0);
}
// auxiliary
void ___c_prmt___pmat_fill(struct pmat *A, double fill_value) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    for(int i = 0; i < m; i++)
        for(int j = 0; j < n; j++)
            blasfeo_dgein1(fill_value, A->bmat, i, j);
}

void ___c_prmt___pmat_set_el(struct pmat *A, int i, int j, double fill_value) {

    blasfeo_dgein1(fill_value, A->bmat, i, j);
}

double ___c_prmt___pmat_get_el(struct pmat *A, int i, int j) {

    blasfeo_dgeex1(A->bmat, i, j);
}

void ___c_prmt___pmat_copy(struct pmat *A, struct pmat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    double value;

    for(int i = 0; i < m; i++)
        for(int j = 0; j < n; j++) {
            value = blasfeo_dgeex1(A->bmat, i, j);
            blasfeo_dgein1(value, B->bmat, i, j);
        }
}

void ___c_prmt___pmat_print(struct pmat *A) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    blasfeo_print_dmat(m, n, A->bmat, 0, 0);
}
