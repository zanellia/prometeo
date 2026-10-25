#include "stdlib.h"
#include "riccati_mass_spring.h"
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
    struct pmat * Ac11 = c_pmt_create_pmat(nm, nm);
    for(int i = 0; i < nm; i++) {
        c_pmt_pmat_set_el(Ac11, i, i, 1.0);
    }

    struct pmat * Ac12 = c_pmt_create_pmat(nm, nm);
    for(int i = 0; i < nm; i++) {
        c_pmt_pmat_set_el(Ac12, i, i, 1.0);
    }

    struct pmat * Ac21 = c_pmt_create_pmat(nm, nm);
    for(int i = 0; i < nm; i++) {
        c_pmt_pmat_set_el(Ac21, i, i, (-2.0));
    }

    for(int i = 0; i < (nm - 1); i++) {
        c_pmt_pmat_set_el(Ac21, (i + 1), i, 1.0);
        c_pmt_pmat_set_el(Ac21, i, (i + 1), 1.0);
    }

    struct pmat * Ac22 = c_pmt_create_pmat(nm, nm);
    for(int i = 0; i < nm; i++) {
        c_pmt_pmat_set_el(Ac22, i, i, 1.0);
    }

    for(int i = 0; i < nm; i++) {
        for(int j = 0; j < nm; j++) {
            c_pmt_pmat_set_el(A, i,                                             j, c_pmt_pmat_get_el(Ac11, i, j));
    }

    }

    for(int i = 0; i < nm; i++) {
        for(int j = 0; j < nm; j++) {
            c_pmt_pmat_set_el(A, i,                                             (nm + j), c_pmt_pmat_get_el(Ac12, i, j));
    }

    }

    for(int i = 0; i < nm; i++) {
        for(int j = 0; j < nm; j++) {
            c_pmt_pmat_set_el(A, (nm + i),                                             j, c_pmt_pmat_get_el(Ac21, i, j));
    }

    }

    for(int i = 0; i < nm; i++) {
        for(int j = 0; j < nm; j++) {
            c_pmt_pmat_set_el(A, (nm + i),                                             (nm + j), c_pmt_pmat_get_el(Ac22, i, j));
    }

    }

    double tmp = 0.0;
    for(int i = 0; i < nx; i++) {
        tmp = c_pmt_pmat_get_el(A, i, i);
        tmp = tmp + 1.0;
        c_pmt_pmat_set_el(A, i, i, tmp);
    }

    struct pmat * B = c_pmt_create_pmat(nx, nu);
    for(int i = 0; i < nu; i++) {
        c_pmt_pmat_set_el(B, (nm + i), i, 1.0);
    }

    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    for(int i = 0; i < nx; i++) {
        c_pmt_pmat_set_el(Q, i, i, 1.0);
    }

    struct pmat * R = c_pmt_create_pmat(nu, nu);
    for(int i = 0; i < nu; i++) {
        c_pmt_pmat_set_el(R, i, i, 1.0);
    }

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
