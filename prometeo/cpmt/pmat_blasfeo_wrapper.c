#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
#include "pmt_heap.h"
#include "pmt_aux.h"
#include <assert.h>
#include <blasfeo_common.h>

void make_int_multiple_of(int num, int *size) { *size = (*size + num - 1) / num * num; }

struct pmat * c_pmt_create_pmat(int m, int n) {	
    // assign current address of global heap to pmat pointer
    struct pmat *pmat = (struct pmat *) ___c_pmt_8_heap;
    void *pmat_address = ___c_pmt_8_heap;
    
    // advance global heap address
    ___c_pmt_8_heap += sizeof(struct pmat);
    
    
    // create (zeroed) blasfeo_dmat and advance global heap
    c_pmt_assign_and_advance_blasfeo_dmat(m, n, &(pmat->bmat));

	return (struct pmat *)(pmat_address);
}

void c_pmt_assign_and_advance_blasfeo_dmat(int m, int n, struct blasfeo_dmat **bmat) {
    // assign current address of global heap to blasfeo dmat pointer
    assert((size_t) ___c_pmt_8_heap % 8 == 0 && "pointer not 8-byte aligned!");
    *bmat = (struct blasfeo_dmat *) ___c_pmt_8_heap;
    //
    // advance global heap address
    ___c_pmt_8_heap += sizeof(struct blasfeo_dmat);

    // assign current address of global heap to memory in blasfeo dmat
    char *pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    assert((size_t) ___c_pmt_64_heap % 64 == 0 && "dmat not 64-byte aligned!");
    blasfeo_create_dmat(m, n, *bmat, ___c_pmt_64_heap);

    // advance global heap address
    int memsize = (*bmat)->memsize;
    // make_int_multiple_of(64, memsize);
    ___c_pmt_64_heap += memsize;	

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

void c_pmt_gemm_nn(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
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

    blasfeo_dgemm_nn(mA, nB, nA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}

struct pmat * _c_pmt_gemm_nn(struct pmat *A, struct pmat *B) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    int nB = B->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;

    
    struct pmat *C = c_pmt_create_pmat(nA, nB);
    struct blasfeo_dmat *bC = C->bmat;

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

    blasfeo_dgemm_nn(mA, nB, nA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bC, 0, 0);
    return C;
}

void c_pmt_gemm_tn(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
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

    blasfeo_dgemm_tn(nA, nB, mA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}

void c_pmt_gemm_nt(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
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

    blasfeo_dgemm_nt(nA, nB, mA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}

void c_pmt_getrf(struct pmat *A, struct pmat *fact, int *ipiv) {
    int mA = A->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bfact = fact->bmat;

    // factorization
    blasfeo_dgetrf_rp(mA, mA, bA, 0, 0, bfact, 0, 0, ipiv);
}

void c_pmt_potrf(struct pmat *A, struct pmat *fact) {
    int mA = A->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bfact = fact->bmat;

    // factorization
    blasfeo_dpotrf_l(mA, bA, 0, 0, bfact, 0, 0);
}

void c_pmt_getrsv(struct pmat *fact, int *ipiv, struct pvec *rhs) {
    int mfact = fact->bmat->m; 
    struct blasfeo_dmat *bfact = fact->bmat;
    struct blasfeo_dvec *brhs = rhs->bvec;

    // permute the r.h.s
    blasfeo_dvecpe(mfact, ipiv, brhs, 0);
    // triangular solves 
    blasfeo_dtrsv_lnu(mfact, bfact, 0, 0, brhs, 0, brhs, 0);
    blasfeo_dtrsv_unn(mfact, bfact, 0, 0, brhs, 0, brhs, 0);
}

void c_pmt_getrsm(struct pmat *fact, int *ipiv, struct pmat *rhs) {
    int mfact = fact->bmat->m; 
    struct blasfeo_dmat *bfact = fact->bmat;
    struct blasfeo_dmat *brhs  = rhs->bmat;

    // permute the r.h.s
    blasfeo_drowpe(mfact, ipiv, brhs);
    // triangular solves 
    blasfeo_dtrsm_llnu(mfact, mfact, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);
    blasfeo_dtrsm_lunn(mfact, mfact, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);
}

struct pmat * _c_pmt_getrsm(struct pmat *A, struct pmat *rhs) {
    int mA = A->bmat->m; 
    struct blasfeo_dmat *brhs  = rhs->bmat;
    struct blasfeo_dmat *bA = A->bmat;

    struct pmat *fact = c_pmt_create_pmat(mA, mA);
    struct blasfeo_dmat *bfact = fact->bmat;

	// permutation indeces
	int *ipiv; int_zeros(&ipiv, mA, 1);
    // factorization
    blasfeo_dgetrf_rp(mA, mA, bA, 0, 0, bfact, 0, 0, ipiv);
    // permute the r.h.s
    blasfeo_drowpe(mA, ipiv, brhs);
    // triangular solves 
    blasfeo_dtrsm_llnu(mA, mA, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);
    blasfeo_dtrsm_lunn(mA, mA, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);
    return rhs;
}

void c_pmt_potrsm(struct pmat *fact, struct pmat *rhs) {
    int mrhs = rhs->bmat->m; 
    int nrhs = rhs->bmat->n; 
    struct blasfeo_dmat *bfact = fact->bmat;
    struct blasfeo_dmat *brhs  = rhs->bmat;
    // struct blasfeo_dmat *bout  = out->bmat;

    // triangular solves 
    blasfeo_dtrsm_llnn(mrhs, nrhs, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);

    // struct pmat * fact_tran = c_pmt_create_pmat(nrhs, nrhs);
    // struct blasfeo_dmat *bfact_tran = fact_tran->bmat;
    blasfeo_dtrtr_l(nrhs, bfact, 0, 0, bfact, 0, 0);
    // blasfeo_dgese(1, 1, 0.0, bfact, 1, 0);
    blasfeo_dtrsm_lunn(mrhs, nrhs, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);
    // blasfeo_dtrsm_lltn(mrhs, nrhs, 1.0, bfact_tran, 0, 0, brhs, 0, 0, brhs, 0, 0);

}

void c_pmt_potrsv(struct pmat *fact, struct pvec *rhs) {
    int mfact = fact->bmat->m; 
    struct blasfeo_dmat *bfact = fact->bmat;
    struct blasfeo_dvec *brhs = rhs->bvec;
    // struct blasfeo_dvec *bout = out->bvec;

    // triangular solves 
    blasfeo_dtrsv_lnu(mfact, bfact, 0, 0, brhs, 0, brhs, 0);
    blasfeo_dtrsv_unn(mfact, bfact, 0, 0, brhs, 0, brhs, 0);
}

void c_pmt_gead(double alpha, struct pmat *A, struct pmat *B) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;

    blasfeo_dgead(mA, nA, alpha, bA, 0, 0, bB, 0, 0);
}


struct pmat * _c_pmt_gead(double alpha, struct pmat *A, struct pmat *B) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;

    struct pmat *C = c_pmt_create_pmat(mA, nA);

    c_pmt_pmat_copy(B, C);
    struct blasfeo_dmat *bC = C->bmat;

    blasfeo_dgead(mA, nA, alpha, bA, 0, 0, bC, 0, 0);
    return C;
}

void c_pmt_gemv_n(struct pmat *A, struct pvec *b, struct pvec *c, struct pvec *d) {
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
void c_pmt_pmat_fill(struct pmat *A, double fill_value) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    blasfeo_dgese(m, n, fill_value, A->bmat, 0, 0);
}

void c_pmt_pmat_set_el(struct pmat *A, int i, int j, double fill_value) {

    blasfeo_dgein1(fill_value, A->bmat, i, j);
}

void c_pmt_gecp(int m, int n, struct pmat *A, int ai, int aj, struct pmat *B, int bi, int bj) {
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    blasfeo_dgecp(m, n, bA, ai, aj, bB, bi, bj);
}

double c_pmt_pmat_get_el(struct pmat *A, int i, int j) {

    blasfeo_dgeex1(A->bmat, i, j);
}

void c_pmt_pmat_copy(struct pmat *A, struct pmat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    double value;


    blasfeo_dgecp(m, n, A->bmat, 0, 0, B->bmat, 0, 0);
    // for(int i = 0; i < m; i++)
    //     for(int j = 0; j < n; j++) {
    //         value = blasfeo_dgeex1(A->bmat, i, j);
    //         blasfeo_dgein1(value, B->bmat, i, j);
    //     }
}

struct pmat * _c_pmt_pmat_copy(struct pmat *A, struct pmat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    double value;

    blasfeo_dgecp(m, n, A->bmat, 0, 0, B->bmat, 0, 0);
    // for(int i = 0; i < m; i++)
    //     for(int j = 0; j < n; j++) {
    //         value = blasfeo_dgeex1(A->bmat, i, j);
    //         blasfeo_dgein1(value, B->bmat, i, j);
    //     }

    return B;
}

void c_pmt_pmat_tran(struct pmat *A, struct pmat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    double value;

    blasfeo_dgetr(m, n, A->bmat, 0, 0, B->bmat, 0, 0);
    // for(int i = 0; i < m; i++)
    //     for(int j = 0; j < n; j++) {
    //         value = blasfeo_dgeex1(A->bmat, i, j);
    //         blasfeo_dgein1(value, B->bmat, j, i);
    //     }
}

struct pmat * _c_pmt_pmat_tran(struct pmat *A) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    struct pmat *B = c_pmt_create_pmat(n, m);
    struct blasfeo_dmat *bB = B->bmat;
    double value;

    blasfeo_dgetr(m, n, A->bmat, 0, 0, B->bmat, 0, 0);
    // for(int i = 0; i < m; i++)
    //     for(int j = 0; j < n; j++) {
    //         value = blasfeo_dgeex1(A->bmat, i, j);
    //         blasfeo_dgein1(value, B->bmat, j, i);
    //     }
    return B;
}

void c_pmt_pmat_vcat(struct pmat *A, struct pmat *B, struct pmat *res) {
    int mA = A->bmat->m;
    int nA = A->bmat->n;
    int mB = B->bmat->m;
    int nB = B->bmat->n;
    double value;

    for(int i = 0; i < mA; i++)
        for(int j = 0; j < nA; j++) {
            value = blasfeo_dgeex1(A->bmat, i, j);
            blasfeo_dgein1(value, res->bmat, i, j);
        }
    for(int i = 0; i < mB; i++)
        for(int j = 0; j < nB; j++) {
            value = blasfeo_dgeex1(B->bmat, i, j);
            blasfeo_dgein1(value, res->bmat, mA + i, j);
        }
}

void c_pmt_pmat_hcat(struct pmat *A, struct pmat *B, struct pmat *res) {
    int mA = A->bmat->m;
    int nA = A->bmat->n;
    int mB = B->bmat->m;
    int nB = B->bmat->n;
    double value;

    for(int i = 0; i < mA; i++)
        for(int j = 0; j < nA; j++) {
            value = blasfeo_dgeex1(A->bmat, i, j);
            blasfeo_dgein1(value, res->bmat, i, j);
        }
    for(int i = 0; i < mB; i++)
        for(int j = 0; j < nB; j++) {
            value = blasfeo_dgeex1(B->bmat, i, j);
            blasfeo_dgein1(value, res->bmat, i, nA + j);
        }
}
void c_pmt_pmat_print(struct pmat *A) {
    int m = A->bmat->m;
    int n = A->bmat->n;

    blasfeo_print_dmat(m, n, A->bmat, 0, 0);
}

