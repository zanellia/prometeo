#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
#include "pmt_heap.h"
#include "pmt_aux.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
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
    // align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    assert((size_t) ___c_pmt_64_heap % 64 == 0 && "dmat not 64-byte aligned!");
    blasfeo_create_dmat(m, n, *bmat, ___c_pmt_64_heap);

    // advance global heap address
    int memsize = (*bmat)->memsize;
    make_int_multiple_of(64, &memsize);
    ___c_pmt_64_heap += memsize;	
    // check the bound before writing to the new memory
    c_pmt_check_heap();

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

    if (B->bmat->m != nA || C->bmat->m != mA || C->bmat->n != nB || D->bmat->m != mA || D->bmat->n != nB)
        c_pmt_dims_error("pmt_gemm_nn");
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

// D <= beta * C + alpha * A * B
void c_pmt_gemm_ab(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D) {
    if (B->bmat->m != A->bmat->n || C->bmat->m != A->bmat->m || C->bmat->n != B->bmat->n ||
            D->bmat->m != A->bmat->m || D->bmat->n != B->bmat->n)
        c_pmt_dims_error("pmt_gemm");
    blasfeo_dgemm_nn(A->bmat->m, B->bmat->n, A->bmat->n, alpha, A->bmat, 0, 0, B->bmat, 0, 0, beta, C->bmat, 0, 0, D->bmat, 0, 0);
}

void c_pmt_gemm_ab_nn(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D) {
    int m = A->bmat->m, n = B->bmat->n, k = A->bmat->n;
    if (k != B->bmat->m || C->bmat->m != m || C->bmat->n != n || D->bmat->m != m || D->bmat->n != n)
        c_pmt_dims_error("pmt_gemm_ab_nn");
    blasfeo_dgemm_nn(m, n, k, alpha, A->bmat, 0, 0, B->bmat, 0, 0, beta, C->bmat, 0, 0, D->bmat, 0, 0);
}

void c_pmt_gemm_ab_nt(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D) {
    int m = A->bmat->m, n = B->bmat->m, k = A->bmat->n;
    if (k != B->bmat->n || C->bmat->m != m || C->bmat->n != n || D->bmat->m != m || D->bmat->n != n)
        c_pmt_dims_error("pmt_gemm_ab_nt");
    blasfeo_dgemm_nt(m, n, k, alpha, A->bmat, 0, 0, B->bmat, 0, 0, beta, C->bmat, 0, 0, D->bmat, 0, 0);
}

void c_pmt_gemm_ab_tn(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D) {
    int m = A->bmat->n, n = B->bmat->n, k = A->bmat->m;
    if (k != B->bmat->m || C->bmat->m != m || C->bmat->n != n || D->bmat->m != m || D->bmat->n != n)
        c_pmt_dims_error("pmt_gemm_ab_tn");
    blasfeo_dgemm_tn(m, n, k, alpha, A->bmat, 0, 0, B->bmat, 0, 0, beta, C->bmat, 0, 0, D->bmat, 0, 0);
}

void c_pmt_gemm_ab_tt(double alpha, struct pmat *A, struct pmat *B, double beta, struct pmat *C, struct pmat *D) {
    int m = A->bmat->n, n = B->bmat->m, k = A->bmat->m;
    if (k != B->bmat->n || C->bmat->m != m || C->bmat->n != n || D->bmat->m != m || D->bmat->n != n)
        c_pmt_dims_error("pmt_gemm_ab_tt");
    blasfeo_dgemm_tt(m, n, k, alpha, A->bmat, 0, 0, B->bmat, 0, 0, beta, C->bmat, 0, 0, D->bmat, 0, 0);
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

    if (B->bmat->m != mA || C->bmat->m != nA || C->bmat->n != nB || D->bmat->m != nA || D->bmat->n != nB)
        c_pmt_dims_error("pmt_gemm_tn");
    blasfeo_dgemm_tn(nA, nB, mA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}

void c_pmt_gemm_nt(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
    int mA = A->bmat->m; 
    int nA = A->bmat->n; 
    int mB = B->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    struct blasfeo_dmat *bC = C->bmat;
    struct blasfeo_dmat *bD = D->bmat;

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

    if (B->bmat->n != nA || C->bmat->m != mA || C->bmat->n != mB || D->bmat->m != mA || D->bmat->n != mB)
        c_pmt_dims_error("pmt_gemm_nt");
    blasfeo_dgemm_nt(mA, mB, nA, 1.0, bA, 0, 0, bB, 0, 0, 1, bC, 0, 0, bD, 0, 0);
}


void c_pmt_trmm_rlnn(struct pmat *A, struct pmat *B, struct pmat *D) {
    int nB = B->bmat->n; 
    int mB = B->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    struct blasfeo_dmat *bD = D->bmat;

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

    if (A->bmat->m != A->bmat->n || nB != A->bmat->m || D->bmat->m != mB || D->bmat->n != nB)
        c_pmt_dims_error("pmt_trmm_rlnn");
    blasfeo_dtrmm_rlnn(mB, nB, 1.0, bA, 0, 0, bB, 0, 0, bD, 0, 0);
}

void c_pmt_syrk_ln(struct pmat *A, struct pmat *B, struct pmat *C, struct pmat *D) {
    int nA = A->bmat->n; 
    int mA = A->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    struct blasfeo_dmat *bD = D->bmat;

    // printf("In dgemm\n");
    // blasfeo_print_dmat(mA, nA, A->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, B->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, C->bmat, 0, 0);
    // blasfeo_print_dmat(mA, nA, D->bmat, 0, 0);

    if (B->bmat->m != mA || B->bmat->n != nA || C->bmat->m != mA || C->bmat->n != mA ||
            D->bmat->m != mA || D->bmat->n != mA)
        c_pmt_dims_error("pmt_syrk_ln");
    blasfeo_dsyrk_ln(mA, nA, 1.0, A->bmat, 0, 0, B->bmat, 0, 0, 1.0, C->bmat, 0, 0, D->bmat, 0, 0);
}

void c_pmt_getrf(struct pmat *A, struct pmat *fact, int *ipiv) {
    int mA = A->bmat->m; 
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bfact = fact->bmat;

    if (A->bmat->n != mA || fact->bmat->m != mA || fact->bmat->n != mA)
        c_pmt_dims_error("pmt_getrf");
    // factorization
    blasfeo_dgetrf_rp(mA, mA, bA, 0, 0, bfact, 0, 0, ipiv);
}

void c_pmt_potrf(struct pmat *A, struct pmat *fact) {
    int mA = A->bmat->m; 
    if (A->bmat->n != mA || fact->bmat->m != mA || fact->bmat->n != mA)
        c_pmt_dims_error("pmt_potrf");
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

    int mfact = fact->bmat->m;
    if (fact->bmat->n != mfact || mrhs != mfact)
        c_pmt_dims_error("pmt_potrsm");

    // triangular solves: L * Y = rhs, then L^T * X = Y
    blasfeo_dtrsm_llnn(mrhs, nrhs, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);

    // dtrsm_lltn is not implemented in the bundled BLASFEO: mirror the lower
    // factor into the upper triangle of fact (mfact x mfact, not nrhs) and use
    // the upper solve instead. Note: this overwrites the upper triangle of fact.
    blasfeo_dtrtr_l(mfact, bfact, 0, 0, bfact, 0, 0);
    blasfeo_dtrsm_lunn(mrhs, nrhs, 1.0, bfact, 0, 0, brhs, 0, 0, brhs, 0, 0);

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
    if (B->bmat->m != mA || B->bmat->n != nA)
        c_pmt_dims_error("pmt_gead");
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

void c_pmt_gecp(int m, int n, struct pmat *A, int ai, int aj, struct pmat *B, int bi, int bj) {
    struct blasfeo_dmat *bA = A->bmat;
    struct blasfeo_dmat *bB = B->bmat;
    blasfeo_dgecp(m, n, bA, ai, aj, bB, bi, bj);
}

void c_pmt_pmat_scale(double alpha, struct pmat *A) {
    blasfeo_dgesc(A->bmat->m, A->bmat->n, alpha, A->bmat, 0, 0);
}

void c_pmt_pmat_copy(struct pmat *A, struct pmat *B) {
    int m = A->bmat->m;
    int n = A->bmat->n;
    if (B->bmat->m != m || B->bmat->n != n)
        c_pmt_dims_error("pmat_copy");
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
    if (B->bmat->m != n || B->bmat->n != m)
        c_pmt_dims_error("pmat_tran");
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

    if (mB != mA || res->bmat->m != mA || res->bmat->n != nA + nB)
        c_pmt_dims_error("pmat_hcat");

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

// resolve the block (i, j, r, c) of M, abort if it is out of range
static void c_pmt_view(const char *fun, struct pmat *M, int *i, int *j, int *r, int *c) {
    if (*r < 0) *r = M->bmat->m - *i;
    if (*c < 0) *c = M->bmat->n - *j;
    if (*i < 0 || *j < 0 || *r <= 0 || *c <= 0 || *i + *r > M->bmat->m || *j + *c > M->bmat->n) {
        fprintf(stderr, "prometeo: %s: block [%d:%d, %d:%d] out of range for a %dx%d pmat\n",
            fun, *i, *i + *r, *j, *j + *c, M->bmat->m, M->bmat->n);
        exit(1);
    }
}

void c_pmt_pmat_copy_view(struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc) {
    c_pmt_view("pmat_copy", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmat_copy", B, &bi, &bj, &br, &bc);
    if (ar != br || ac != bc) c_pmt_dims_error("pmat_copy");
    blasfeo_dgecp(ar, ac, A->bmat, ai, aj, B->bmat, bi, bj);
}

void c_pmt_pmat_tran_view(struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc) {
    c_pmt_view("pmat_tran", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmat_tran", B, &bi, &bj, &br, &bc);
    if (ar != bc || ac != br) c_pmt_dims_error("pmat_tran");
    blasfeo_dgetr(ar, ac, A->bmat, ai, aj, B->bmat, bi, bj);
}

void c_pmt_pmat_fill_view(double value, struct pmat *A, int ai, int aj, int ar, int ac) {
    c_pmt_view("pmat_fill", A, &ai, &aj, &ar, &ac);
    blasfeo_dgese(ar, ac, value, A->bmat, ai, aj);
}

void c_pmt_pmat_scale_view(double alpha, struct pmat *A, int ai, int aj, int ar, int ac) {
    c_pmt_view("pmat_scale", A, &ai, &aj, &ar, &ac);
    blasfeo_dgesc(ar, ac, alpha, A->bmat, ai, aj);
}

void c_pmt_gead_view(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc) {
    c_pmt_view("pmt_gead", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmt_gead", B, &bi, &bj, &br, &bc);
    if (ar != br || ac != bc) c_pmt_dims_error("pmt_gead");
    blasfeo_dgead(ar, ac, alpha, A->bmat, ai, aj, B->bmat, bi, bj);
}

void c_pmt_gemm_view_nn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_view("pmt_gemm_nn", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmt_gemm_nn", B, &bi, &bj, &br, &bc);
    c_pmt_view("pmt_gemm_nn", C, &ci, &cj, &cr, &cc);
    c_pmt_view("pmt_gemm_nn", D, &di, &dj, &dr, &dc);
    if (ac != br || cr != ar || cc != bc || dr != ar || dc != bc)
        c_pmt_dims_error("pmt_gemm_nn");
    blasfeo_dgemm_nn(ar, bc, ac, alpha, A->bmat, ai, aj, B->bmat, bi, bj, beta, C->bmat, ci, cj, D->bmat, di, dj);
}

void c_pmt_gemm_view_nt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_view("pmt_gemm_nt", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmt_gemm_nt", B, &bi, &bj, &br, &bc);
    c_pmt_view("pmt_gemm_nt", C, &ci, &cj, &cr, &cc);
    c_pmt_view("pmt_gemm_nt", D, &di, &dj, &dr, &dc);
    if (ac != bc || cr != ar || cc != br || dr != ar || dc != br)
        c_pmt_dims_error("pmt_gemm_nt");
    blasfeo_dgemm_nt(ar, br, ac, alpha, A->bmat, ai, aj, B->bmat, bi, bj, beta, C->bmat, ci, cj, D->bmat, di, dj);
}

void c_pmt_gemm_view_tn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_view("pmt_gemm_tn", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmt_gemm_tn", B, &bi, &bj, &br, &bc);
    c_pmt_view("pmt_gemm_tn", C, &ci, &cj, &cr, &cc);
    c_pmt_view("pmt_gemm_tn", D, &di, &dj, &dr, &dc);
    if (ar != br || cr != ac || cc != bc || dr != ac || dc != bc)
        c_pmt_dims_error("pmt_gemm_tn");
    blasfeo_dgemm_tn(ac, bc, ar, alpha, A->bmat, ai, aj, B->bmat, bi, bj, beta, C->bmat, ci, cj, D->bmat, di, dj);
}

void c_pmt_gemm_view_tt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, double beta, struct pmat *C, int ci, int cj, int cr, int cc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_view("pmt_gemm_tt", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmt_gemm_tt", B, &bi, &bj, &br, &bc);
    c_pmt_view("pmt_gemm_tt", C, &ci, &cj, &cr, &cc);
    c_pmt_view("pmt_gemm_tt", D, &di, &dj, &dr, &dc);
    if (ar != bc || cr != ac || cc != br || dr != ac || dc != br)
        c_pmt_dims_error("pmt_gemm_tt");
    blasfeo_dgemm_tt(ac, br, ar, alpha, A->bmat, ai, aj, B->bmat, bi, bj, beta, C->bmat, ci, cj, D->bmat, di, dj);
}

// resolve the slice (i, r) of v, abort if it is out of range
static void c_pmt_vview(const char *fun, struct pvec *v, int *i, int *r) {
    if (*r < 0) *r = v->bvec->m - *i;
    if (*i < 0 || *r <= 0 || *i + *r > v->bvec->m) {
        fprintf(stderr, "prometeo: %s: slice [%d:%d] out of range for a pvec of size %d\n",
            fun, *i, *i + *r, v->bvec->m);
        exit(1);
    }
}

void c_pmt_pvec_copy_view(struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr) {
    c_pmt_vview("pvec_copy", x, &xi, &xr);
    c_pmt_vview("pvec_copy", y, &yi, &yr);
    if (xr != yr) c_pmt_dims_error("pvec_copy");
    blasfeo_dveccp(xr, x->bvec, xi, y->bvec, yi);
}

void c_pmt_pvec_fill_view(double value, struct pvec *x, int xi, int xr) {
    c_pmt_vview("pvec_fill", x, &xi, &xr);
    blasfeo_dvecse(xr, value, x->bvec, xi);
}

void c_pmt_pvec_scale_view(double alpha, struct pvec *x, int xi, int xr) {
    c_pmt_vview("pvec_scale", x, &xi, &xr);
    blasfeo_dvecsc(xr, alpha, x->bvec, xi);
}

// y <= y + alpha * x
void c_pmt_pvec_axpy_view(double alpha, struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr) {
    c_pmt_vview("pvec_axpy", x, &xi, &xr);
    c_pmt_vview("pvec_axpy", y, &yi, &yr);
    if (xr != yr) c_pmt_dims_error("pvec_axpy");
    blasfeo_daxpy(xr, alpha, x->bvec, xi, y->bvec, yi, y->bvec, yi);
}

double c_pmt_pvec_dot_view(struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr) {
    c_pmt_vview("pvec_dot", x, &xi, &xr);
    c_pmt_vview("pvec_dot", y, &yi, &yr);
    if (xr != yr) c_pmt_dims_error("pvec_dot");
    return blasfeo_ddot(xr, x->bvec, xi, y->bvec, yi);
}

// z <= beta * y + alpha * op(A) x
void c_pmt_gemv_view_n(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pvec *x, int xi, int xr, double beta, struct pvec *y, int yi, int yr, struct pvec *z, int zi, int zr) {
    c_pmt_view("pmt_gemv_n", A, &ai, &aj, &ar, &ac);
    c_pmt_vview("pmt_gemv_n", x, &xi, &xr);
    c_pmt_vview("pmt_gemv_n", y, &yi, &yr);
    c_pmt_vview("pmt_gemv_n", z, &zi, &zr);
    if (xr != ac || yr != ar || zr != ar) c_pmt_dims_error("pmt_gemv_n");
    blasfeo_dgemv_n(ar, ac, alpha, A->bmat, ai, aj, x->bvec, xi, beta, y->bvec, yi, z->bvec, zi);
}

// z <= beta * y + alpha * op(A) x
void c_pmt_gemv_view_t(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pvec *x, int xi, int xr, double beta, struct pvec *y, int yi, int yr, struct pvec *z, int zi, int zr) {
    c_pmt_view("pmt_gemv_t", A, &ai, &aj, &ar, &ac);
    c_pmt_vview("pmt_gemv_t", x, &xi, &xr);
    c_pmt_vview("pmt_gemv_t", y, &yi, &yr);
    c_pmt_vview("pmt_gemv_t", z, &zi, &zr);
    if (xr != ar || yr != ac || zr != ac) c_pmt_dims_error("pmt_gemv_t");
    blasfeo_dgemv_t(ar, ac, alpha, A->bmat, ai, aj, x->bvec, xi, beta, y->bvec, yi, z->bvec, zi);
}

// x <= (L L^T)^-1 x, L lower triangular (not modified)
void c_pmt_potrsv_view(struct pmat *L, struct pvec *x, int xi, int xr) {
    c_pmt_vview("pmt_potrsv", x, &xi, &xr);
    if (L->bmat->m != L->bmat->n || L->bmat->m != xr) c_pmt_dims_error("pmt_potrsv");
    blasfeo_dtrsv_lnn(xr, L->bmat, 0, 0, x->bvec, xi, x->bvec, xi);
    blasfeo_dtrsv_ltn(xr, L->bmat, 0, 0, x->bvec, xi, x->bvec, xi);
}

// D <= D + alpha * op(A) .* op(B) (the same operations, in the same order, as
// _mul_view in the Python runtime)
static void c_pmt_pmat_mul_view(int ta, int tb, double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_view("pmat_mul", A, &ai, &aj, &ar, &ac);
    c_pmt_view("pmat_mul", B, &bi, &bj, &br, &bc);
    c_pmt_view("pmat_mul", D, &di, &dj, &dr, &dc);
    if ((ta ? ac : ar) != dr || (ta ? ar : ac) != dc || (tb ? bc : br) != dr || (tb ? br : bc) != dc)
        c_pmt_dims_error("pmat_mul");
    D->bmat->use_dA = 0;
    for (int j = 0; j < dc; j++) {
        for (int i = 0; i < dr; i++) {
            double a = ta ? BLASFEO_DMATEL(A->bmat, ai + j, aj + i) : BLASFEO_DMATEL(A->bmat, ai + i, aj + j);
            double b = tb ? BLASFEO_DMATEL(B->bmat, bi + j, bj + i) : BLASFEO_DMATEL(B->bmat, bi + i, bj + j);
            BLASFEO_DMATEL(D->bmat, di + i, dj + j) = BLASFEO_DMATEL(D->bmat, di + i, dj + j) + alpha * (a * b);
        }
    }
}

void c_pmt_pmat_mul_view_nn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_pmat_mul_view(0, 0, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc);
}

void c_pmt_pmat_mul_view_nt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_pmat_mul_view(0, 1, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc);
}

void c_pmt_pmat_mul_view_tn(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_pmat_mul_view(1, 0, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc);
}

void c_pmt_pmat_mul_view_tt(double alpha, struct pmat *A, int ai, int aj, int ar, int ac, struct pmat *B, int bi, int bj, int br, int bc, struct pmat *D, int di, int dj, int dr, int dc) {
    c_pmt_pmat_mul_view(1, 1, alpha, A, ai, aj, ar, ac, B, bi, bj, br, bc, D, di, dj, dr, dc);
}

// z <= z + alpha * x .* y
void c_pmt_pvec_mul_view(double alpha, struct pvec *x, int xi, int xr, struct pvec *y, int yi, int yr, struct pvec *z, int zi, int zr) {
    c_pmt_vview("pvec_mul", x, &xi, &xr);
    c_pmt_vview("pvec_mul", y, &yi, &yr);
    c_pmt_vview("pvec_mul", z, &zi, &zr);
    if (xr != zr || yr != zr) c_pmt_dims_error("pvec_mul");
    for (int i = 0; i < zr; i++)
        BLASFEO_DVECEL(z->bvec, zi + i) = BLASFEO_DVECEL(z->bvec, zi + i) +
            alpha * (BLASFEO_DVECEL(x->bvec, xi + i) * BLASFEO_DVECEL(y->bvec, yi + i));
}

// resolve the row (row = 1) or column A[i, j:j + r] or A[i:i + r, j]
static void c_pmt_line(const char *fun, struct pmat *A, int i, int j, int *r, int row) {
    if (*r < 0) *r = row ? A->bmat->n - j : A->bmat->m - i;
    int end_i = row ? i + 1 : i + *r, end_j = row ? j + *r : j + 1;
    if (i < 0 || j < 0 || *r <= 0 || end_i > A->bmat->m || end_j > A->bmat->n) {
        if (row)
            fprintf(stderr, "prometeo: %s: [%d, %d:%d] out of range for a %dx%d pmat\n",
                fun, i, j, j + *r, A->bmat->m, A->bmat->n);
        else
            fprintf(stderr, "prometeo: %s: [%d:%d, %d] out of range for a %dx%d pmat\n",
                fun, i, i + *r, j, A->bmat->m, A->bmat->n);
        exit(1);
    }
}

void c_pmt_pmat_getrow_view(struct pmat *A, int i, int j, int r, struct pvec *x, int xi, int xr) {
    c_pmt_line("pmat_getrow", A, i, j, &r, 1);
    c_pmt_vview("pmat_getrow", x, &xi, &xr);
    if (r != xr) c_pmt_dims_error("pmat_getrow");
    blasfeo_drowex(r, 1.0, A->bmat, i, j, x->bvec, xi);
}

void c_pmt_pmat_getcol_view(struct pmat *A, int i, int j, int r, struct pvec *x, int xi, int xr) {
    c_pmt_line("pmat_getcol", A, i, j, &r, 0);
    c_pmt_vview("pmat_getcol", x, &xi, &xr);
    if (r != xr) c_pmt_dims_error("pmat_getcol");
    blasfeo_dcolex(r, A->bmat, i, j, x->bvec, xi);
}

void c_pmt_pmat_setrow_view(struct pvec *x, int xi, int xr, struct pmat *A, int i, int j, int r) {
    c_pmt_line("pmat_setrow", A, i, j, &r, 1);
    c_pmt_vview("pmat_setrow", x, &xi, &xr);
    if (r != xr) c_pmt_dims_error("pmat_setrow");
    blasfeo_drowin(r, 1.0, x->bvec, xi, A->bmat, i, j);
    A->bmat->use_dA = 0;
}

void c_pmt_pmat_setcol_view(struct pvec *x, int xi, int xr, struct pmat *A, int i, int j, int r) {
    c_pmt_line("pmat_setcol", A, i, j, &r, 0);
    c_pmt_vview("pmat_setcol", x, &xi, &xr);
    if (r != xr) c_pmt_dims_error("pmat_setcol");
    blasfeo_dcolin(r, x->bvec, xi, A->bmat, i, j);
    A->bmat->use_dA = 0;
}
