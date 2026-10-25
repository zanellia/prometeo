#include "stdlib.h"
#include "test.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;
void * ___c_pmt_8_heap_end;
void * ___c_pmt_64_heap_end;

#include "prometeo.h"

void qp_data_constructor(struct qp_data *object){
    object->_Z8__init__ = &_Z8__init__qp_data_impl;
    object->_Z9factorize = &_Z9factorizeqp_data_impl;
	object->_Z8__init__(object);

}



void _Z8__init__qp_data_impl(qp_data *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->A[0] = c_pmt_create_pmat(2, 2);
    self->A[1] = c_pmt_create_pmat(2, 2);
    self->A[2] = c_pmt_create_pmat(2, 2);
    self->A[3] = c_pmt_create_pmat(2, 2);
    self->A[4] = c_pmt_create_pmat(2, 2);
    self->B[0] = c_pmt_create_pmat(2, 2);
    self->B[1] = c_pmt_create_pmat(2, 2);
    self->B[2] = c_pmt_create_pmat(2, 2);
    self->B[3] = c_pmt_create_pmat(2, 2);
    self->B[4] = c_pmt_create_pmat(2, 2);
    self->Q[0] = c_pmt_create_pmat(2, 2);
    self->Q[1] = c_pmt_create_pmat(2, 2);
    self->Q[2] = c_pmt_create_pmat(2, 2);
    self->Q[3] = c_pmt_create_pmat(2, 2);
    self->Q[4] = c_pmt_create_pmat(2, 2);
    self->R[0] = c_pmt_create_pmat(2, 2);
    self->R[1] = c_pmt_create_pmat(2, 2);
    self->R[2] = c_pmt_create_pmat(2, 2);
    self->R[3] = c_pmt_create_pmat(2, 2);
    self->R[4] = c_pmt_create_pmat(2, 2);
    self->P[0] = c_pmt_create_pmat(2, 2);
    self->P[1] = c_pmt_create_pmat(2, 2);
    self->P[2] = c_pmt_create_pmat(2, 2);
    self->P[3] = c_pmt_create_pmat(2, 2);
    self->P[4] = c_pmt_create_pmat(2, 2);
    self->fact[0] = c_pmt_create_pmat(2, 2);
    self->fact[1] = c_pmt_create_pmat(2, 2);
    self->fact[2] = c_pmt_create_pmat(2, 2);
    self->fact[3] = c_pmt_create_pmat(2, 2);
    self->fact[4] = c_pmt_create_pmat(2, 2);
}


void _Z9factorizeqp_data_impl(qp_data *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * M = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Mu = c_pmt_create_pmat(nu, nu);
    struct pmat * Mxut = c_pmt_create_pmat(nu, nxu);
    struct pmat * Mxx = c_pmt_create_pmat(nx, nx);
    struct pmat * Mxu = c_pmt_create_pmat(nxu, nu);
    struct pmat * Lu = c_pmt_create_pmat(nu, nu);
    struct pmat * Lxu = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    struct pmat * BA = c_pmt_create_pmat(nx, nxu);
    struct pmat * BAtP = c_pmt_create_pmat(nxu, nx);
    c_pmt_pmat_copy(self->Q[N - 1], self->P[N - 1]);
    for(int i = 1; i < N; i+=1) {
        c_pmt_pmat_hcat(self->B[N - i], self->A[N - i], BA);
        c_pmt_gemm_tn(BA, self->P[N - i], BAtP, BAtP);
        c_pmt_pmat_copy(self->Q[N - i], Q);
        c_pmt_pmat_copy(self->R[N - i], R);
        c_pmt_gecp(nu-0, nu-0, R, 0, 0, M, 0, 0);
        c_pmt_gecp((nu + nx)-nu, (nu + nx)-nu, Q, 0, 0, M, nu, nu);
        for(int j = 0; j < nu; j++) {
            for(int k = 0; k < nu; k++) {
                c_pmt_pmat_set_el(M, j,                                             k, c_pmt_pmat_get_el(R, j, k));
    }

    }

        for(int j = 0; j < nx; j++) {
            for(int k = 0; k < nx; k++) {
                c_pmt_pmat_set_el(M, (nu + j),                                             (nu + k), c_pmt_pmat_get_el(Q, j, k));
    }

    }

        c_pmt_gemm_nn(BAtP, BA, M, M);
        for(int j = 0; j < nu; j++) {
            for(int k = 0; k < nu; k++) {
                c_pmt_pmat_set_el(Mu, j,                                             k, c_pmt_pmat_get_el(M, j, k));
    }

    }

        c_pmt_potrf(Mu, Lu);
        for(int j = 0; j < nx; j++) {
            for(int k = 0; k < nx; k++) {
                c_pmt_pmat_set_el(Mxut, k,                                             (nu + j), c_pmt_pmat_get_el(M, j, k));
    }

    }

        for(int j = 0; j < nx; j++) {
            for(int k = 0; k < nx; k++) {
                c_pmt_pmat_set_el(Mxx, k,                                             j, c_pmt_pmat_get_el(M, (nu + j), (nu + k)));
    }

    }

        c_pmt_potrsm(Lu, Mxut);
        c_pmt_pmat_tran(Mxut, Mxu);
        c_pmt_gemm_nn(Mxut, Mxu, self->P[N - i - 1], self->P[N - i - 1]);
        c_pmt_gead(-1.0, self->P[N - i - 1], Mxx);
        c_pmt_pmat_copy(Mxx, self->P[N - i - 1]);
        c_pmt_pmat_print(self->P[N - i - 1]);
    }

}int main() {
    prometeo_timer timer0, timer1;
    double total_time, execution_time;
    prometeo_tic(&timer0);
    ___c_pmt_8_heap = malloc(HEAP8_SIZE); 
    ___c_pmt_8_heap_head = ___c_pmt_8_heap;
    ___c_pmt_8_heap_end = (char *) ___c_pmt_8_heap + HEAP8_SIZE;
    char * pmem_ptr = (char *)___c_pmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_pmt_8_heap = pmem_ptr;
    ___c_pmt_64_heap = malloc(HEAP64_SIZE);
    ___c_pmt_64_heap_head = ___c_pmt_64_heap;
    ___c_pmt_64_heap_end = (char *) ___c_pmt_64_heap + HEAP64_SIZE;
    pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    prometeo_tic(&timer1);
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * M = c_pmt_create_pmat(n, n);
    struct pvec * a = c_pmt_create_pvec(n);
    c_pmt_pvec_set_el(a, 1, 3.0);
    double d = 10.0;
    c_pmt_pmat_set_el(M, 0, 1, d);
    c_pmt_pmat_set_el(M, 0, 1, 1.0);
    d = c_pmt_pmat_get_el(M, 0, 1);
    c_pmt_pvec_set_el(a, 0, d);
    c_pmt_pvec_set_el(a, 0, 1.0);
    d = c_pmt_pvec_get_el(a, 0);
    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(M, 0,                                             i, c_pmt_pmat_get_el(M, 0, i));
    }

    c_pmt_pvec_set_el(a, 0, c_pmt_pvec_get_el(a, 1));
    c_pmt_pmat_set_el(M, 0,                                             2, c_pmt_pvec_get_el(a, 1));
    struct pmat * A = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(A, 0, 0, 0.8);
    c_pmt_pmat_set_el(A, 0, 1, 0.1);
    c_pmt_pmat_set_el(A, 1, 0, 0.0);
    c_pmt_pmat_set_el(A, 1, 1, 0.8);
    struct pmat * B = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_set_el(B, 0, 0, 1.0);
    c_pmt_pmat_set_el(B, 0, 1, 0.0);
    c_pmt_pmat_set_el(B, 1, 0, 0.0);
    c_pmt_pmat_set_el(B, 1, 1, 1.0);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(Q, 0, 0, 1.0);
    c_pmt_pmat_set_el(Q, 0, 1, 0.0);
    c_pmt_pmat_set_el(Q, 1, 0, 0.0);
    c_pmt_pmat_set_el(Q, 1, 1, 1.0);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    c_pmt_pmat_set_el(R, 0, 0, 1.0);
    c_pmt_pmat_set_el(R, 0, 1, 0.0);
    c_pmt_pmat_set_el(R, 1, 0, 0.0);
    c_pmt_pmat_set_el(R, 1, 1, 1.0);
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
