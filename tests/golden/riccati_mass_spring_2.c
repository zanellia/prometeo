#include "stdlib.h"
#include "riccati_mass_spring_2.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;

#include "prometeo.h"

void qp_data_constructor(struct qp_data *object){
    object->_Z8__init__ = &_Z8__init__qp_data_impl;
    object->_Z9factorize = &_Z9factorizeqp_data_impl;
	object->_Z8__init__(object);

}



void _Z8__init__qp_data_impl(qp_data *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->A[0] = c_pmt_create_pmat(8, 8);
    self->A[1] = c_pmt_create_pmat(8, 8);
    self->A[2] = c_pmt_create_pmat(8, 8);
    self->A[3] = c_pmt_create_pmat(8, 8);
    self->A[4] = c_pmt_create_pmat(8, 8);
    self->B[0] = c_pmt_create_pmat(8, 8);
    self->B[1] = c_pmt_create_pmat(8, 8);
    self->B[2] = c_pmt_create_pmat(8, 8);
    self->B[3] = c_pmt_create_pmat(8, 8);
    self->B[4] = c_pmt_create_pmat(8, 8);
    self->Q[0] = c_pmt_create_pmat(8, 8);
    self->Q[1] = c_pmt_create_pmat(8, 8);
    self->Q[2] = c_pmt_create_pmat(8, 8);
    self->Q[3] = c_pmt_create_pmat(8, 8);
    self->Q[4] = c_pmt_create_pmat(8, 8);
    self->R[0] = c_pmt_create_pmat(8, 8);
    self->R[1] = c_pmt_create_pmat(8, 8);
    self->R[2] = c_pmt_create_pmat(8, 8);
    self->R[3] = c_pmt_create_pmat(8, 8);
    self->R[4] = c_pmt_create_pmat(8, 8);
    self->P[0] = c_pmt_create_pmat(8, 8);
    self->P[1] = c_pmt_create_pmat(8, 8);
    self->P[2] = c_pmt_create_pmat(8, 8);
    self->P[3] = c_pmt_create_pmat(8, 8);
    self->P[4] = c_pmt_create_pmat(8, 8);
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z9factorizeqp_data_impl(qp_data *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * M = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Mxx = c_pmt_create_pmat(nx, nx);
    struct pmat * L = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    struct pmat * BA = c_pmt_create_pmat(nx, nxu);
    struct pmat * BAtP = c_pmt_create_pmat(nxu, nx);
    c_pmt_pmat_copy(self->Q[N - 1], self->P[N - 1]);
    c_pmt_pmat_hcat(self->B[N - 1], self->A[N - 1], BA);
    c_pmt_pmat_copy(self->Q[N - 1], Q);
    c_pmt_pmat_copy(self->R[N - 1], R);
    for(int i = 1; i < N; i+=1) {
        c_pmt_pmat_fill(BAtP, 0.0);
        c_pmt_gemm_tn(BA, self->P[N - i], BAtP, BAtP);
        c_pmt_pmat_fill(M, 0.0);
        c_pmt_gecp(nu-0, nu-0, R, 0, 0, M, 0, 0);
        c_pmt_gecp((nu + nx)-nu, (nu + nx)-nu, Q, 0, 0, M, nu, nu);
        c_pmt_gemm_nn(BAtP, BA, M, M);
        c_pmt_pmat_fill(L, 0.0);
        c_pmt_potrf(M, L);
        c_pmt_gecp(nx-0, nx-0, L, nu, nu, Mxx, 0, 0);
        c_pmt_gemm_nt(Mxx, Mxx, self->P[N - i - 1], self->P[N - i - 1]);
        c_pmt_pmat_print(self->P[N - i - 1]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}int main() {
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

    struct pmat * A = c_pmt_create_pmat(nx, nx);
    struct pmat * Ac11 = c_pmt_create_pmat(nm, nm);
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

    struct qp_data qp___;
    struct qp_data * qp= &qp___;
    qp_data_constructor(qp); //
    for(int i = 0; i < N; i++) {
        qp->A[i] = A;
    }

    for(int i = 0; i < N; i++) {
        qp->B[i] = B;
    }

    for(int i = 0; i < N; i++) {
        qp->Q[i] = Q;
    }

    for(int i = 0; i < N; i++) {
        qp->R[i] = R;
    }

    qp->_Z9factorize(qp);
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
