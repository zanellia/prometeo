#include "stdlib.h"
#include "riccati_array.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;

#include "prometeo.h"
int main() {
    prometeo_timer timer0, timer1;
    double total_time, execution_time;
    prometeo_tic(&timer0);
    ___c_pmt_8_heap = malloc(HEAP8_SIZE); 
    ___c_pmt_8_heap_head = ___c_pmt_8_heap;
    char * pmem_ptr = (char *)___c_pmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_pmt_8_heap = pmem_ptr;
    ___c_pmt_64_heap = malloc(HEAP64_SIZE);
    ___c_pmt_64_heap_head = ___c_pmt_64_heap;
    pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    prometeo_tic(&timer1);
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    int nrep = 10000;
    struct pmat * A = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(A, 0, 0, 0.8);
    c_pmt_pmat_set_el(A, 0, 1, 0.1);
    c_pmt_pmat_set_el(A, 1, 0, 0.3);
    c_pmt_pmat_set_el(A, 1, 1, 0.8);
    struct pmat * B = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_set_el(B, 0, 0, 1.0);
    c_pmt_pmat_set_el(B, 1, 1, 1.0);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(Q, 0, 0, 1.0);
    c_pmt_pmat_set_el(Q, 1, 1, 1.0);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    c_pmt_pmat_set_el(R, 0, 0, 1.0);
    c_pmt_pmat_set_el(R, 1, 1, 1.0);
    struct pmat * RSQ = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Lxx = c_pmt_create_pmat(nx, nx);
    struct pmat * M = c_pmt_create_pmat(nxu, nxu);
    struct pmat * w_nxu_nx = c_pmt_create_pmat(nxu, nx);
    struct pmat * BAt = c_pmt_create_pmat(nxu, nx);
    struct pmat * BA = c_pmt_create_pmat(nx, nxu);
    c_pmt_pmat_hcat(B, A, BA);
    c_pmt_pmat_tran(BA, BAt);
    c_pmt_gecp(nu-0, nu-0, R, 0, 0, RSQ, 0, 0);
    c_pmt_gecp((nu + nx)-nu, (nu + nx)-nu, Q, 0, 0, RSQ, nu, nu);
    for(int i = 0; i < nrep; i++) {
        c_pmt_potrf(Q, Lxx);
        c_pmt_gecp((nu + nx)-nu, (nu + nx)-nu, Lxx, 0, 0, M, nu, nu);
        for(int i = 1; i < N; i+=1) {
            c_pmt_trmm_rlnn(Lxx, BAt, w_nxu_nx);
            c_pmt_syrk_ln(w_nxu_nx, w_nxu_nx, RSQ, M);
            c_pmt_potrf(M, M);
            c_pmt_gecp(nx-0, nx-0, M, nu, nu, Lxx, 0, 0);
    }

    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

	execution_time = prometeo_toc(&timer1);
	printf("execution time:%fs\n", execution_time);
	free(___c_pmt_8_heap_head);
	free(___c_pmt_64_heap_head);
	total_time = prometeo_toc(&timer0);
	printf("total time:%fs", total_time);
	return 0;
}
