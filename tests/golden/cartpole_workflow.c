#include "stdlib.h"
#include "cartpole_workflow.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;
void * ___c_pmt_8_heap_end;
void * ___c_pmt_64_heap_end;

#include "prometeo.h"

double h = 0.05;
int n_sqp = 20;
double tol = 1e-10;
int n_mpc = 60;
int n_dare = 300;
void SQP_constructor(struct SQP *object){
    object->_Z8__init__ = &_Z8__init__SQP_impl;
    object->_Z13terminal_cost = &_Z13terminal_costSQP_impl;
    object->_Z9linearize = &_Z9linearizeSQP_impl;
    object->_Z7riccati = &_Z7riccatiSQP_impl;
    object->_Z7iterate = &_Z7iterateSQP_impl;
    object->_Z5shift = &_Z5shiftSQP_impl;
	object->_Z8__init__(object);

}



void _Z8__init__SQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->xs[0] = c_pmt_create_pmat(nx, 1);
    self->xs[1] = c_pmt_create_pmat(nx, 1);
    self->xs[2] = c_pmt_create_pmat(nx, 1);
    self->xs[3] = c_pmt_create_pmat(nx, 1);
    self->xs[4] = c_pmt_create_pmat(nx, 1);
    self->xs[5] = c_pmt_create_pmat(nx, 1);
    self->xs[6] = c_pmt_create_pmat(nx, 1);
    self->xs[7] = c_pmt_create_pmat(nx, 1);
    self->xs[8] = c_pmt_create_pmat(nx, 1);
    self->xs[9] = c_pmt_create_pmat(nx, 1);
    self->xs[10] = c_pmt_create_pmat(nx, 1);
    self->xs[11] = c_pmt_create_pmat(nx, 1);
    self->xs[12] = c_pmt_create_pmat(nx, 1);
    self->xs[13] = c_pmt_create_pmat(nx, 1);
    self->xs[14] = c_pmt_create_pmat(nx, 1);
    self->xs[15] = c_pmt_create_pmat(nx, 1);
    self->xs[16] = c_pmt_create_pmat(nx, 1);
    self->xs[17] = c_pmt_create_pmat(nx, 1);
    self->xs[18] = c_pmt_create_pmat(nx, 1);
    self->xs[19] = c_pmt_create_pmat(nx, 1);
    self->xs[20] = c_pmt_create_pmat(nx, 1);
    self->us[0] = c_pmt_create_pmat(nu, 1);
    self->us[1] = c_pmt_create_pmat(nu, 1);
    self->us[2] = c_pmt_create_pmat(nu, 1);
    self->us[3] = c_pmt_create_pmat(nu, 1);
    self->us[4] = c_pmt_create_pmat(nu, 1);
    self->us[5] = c_pmt_create_pmat(nu, 1);
    self->us[6] = c_pmt_create_pmat(nu, 1);
    self->us[7] = c_pmt_create_pmat(nu, 1);
    self->us[8] = c_pmt_create_pmat(nu, 1);
    self->us[9] = c_pmt_create_pmat(nu, 1);
    self->us[10] = c_pmt_create_pmat(nu, 1);
    self->us[11] = c_pmt_create_pmat(nu, 1);
    self->us[12] = c_pmt_create_pmat(nu, 1);
    self->us[13] = c_pmt_create_pmat(nu, 1);
    self->us[14] = c_pmt_create_pmat(nu, 1);
    self->us[15] = c_pmt_create_pmat(nu, 1);
    self->us[16] = c_pmt_create_pmat(nu, 1);
    self->us[17] = c_pmt_create_pmat(nu, 1);
    self->us[18] = c_pmt_create_pmat(nu, 1);
    self->us[19] = c_pmt_create_pmat(nu, 1);
    self->A[0] = c_pmt_create_pmat(nx, nx);
    self->A[1] = c_pmt_create_pmat(nx, nx);
    self->A[2] = c_pmt_create_pmat(nx, nx);
    self->A[3] = c_pmt_create_pmat(nx, nx);
    self->A[4] = c_pmt_create_pmat(nx, nx);
    self->A[5] = c_pmt_create_pmat(nx, nx);
    self->A[6] = c_pmt_create_pmat(nx, nx);
    self->A[7] = c_pmt_create_pmat(nx, nx);
    self->A[8] = c_pmt_create_pmat(nx, nx);
    self->A[9] = c_pmt_create_pmat(nx, nx);
    self->A[10] = c_pmt_create_pmat(nx, nx);
    self->A[11] = c_pmt_create_pmat(nx, nx);
    self->A[12] = c_pmt_create_pmat(nx, nx);
    self->A[13] = c_pmt_create_pmat(nx, nx);
    self->A[14] = c_pmt_create_pmat(nx, nx);
    self->A[15] = c_pmt_create_pmat(nx, nx);
    self->A[16] = c_pmt_create_pmat(nx, nx);
    self->A[17] = c_pmt_create_pmat(nx, nx);
    self->A[18] = c_pmt_create_pmat(nx, nx);
    self->A[19] = c_pmt_create_pmat(nx, nx);
    self->B[0] = c_pmt_create_pmat(nx, nu);
    self->B[1] = c_pmt_create_pmat(nx, nu);
    self->B[2] = c_pmt_create_pmat(nx, nu);
    self->B[3] = c_pmt_create_pmat(nx, nu);
    self->B[4] = c_pmt_create_pmat(nx, nu);
    self->B[5] = c_pmt_create_pmat(nx, nu);
    self->B[6] = c_pmt_create_pmat(nx, nu);
    self->B[7] = c_pmt_create_pmat(nx, nu);
    self->B[8] = c_pmt_create_pmat(nx, nu);
    self->B[9] = c_pmt_create_pmat(nx, nu);
    self->B[10] = c_pmt_create_pmat(nx, nu);
    self->B[11] = c_pmt_create_pmat(nx, nu);
    self->B[12] = c_pmt_create_pmat(nx, nu);
    self->B[13] = c_pmt_create_pmat(nx, nu);
    self->B[14] = c_pmt_create_pmat(nx, nu);
    self->B[15] = c_pmt_create_pmat(nx, nu);
    self->B[16] = c_pmt_create_pmat(nx, nu);
    self->B[17] = c_pmt_create_pmat(nx, nu);
    self->B[18] = c_pmt_create_pmat(nx, nu);
    self->B[19] = c_pmt_create_pmat(nx, nu);
    self->b[0] = c_pmt_create_pmat(nx, 1);
    self->b[1] = c_pmt_create_pmat(nx, 1);
    self->b[2] = c_pmt_create_pmat(nx, 1);
    self->b[3] = c_pmt_create_pmat(nx, 1);
    self->b[4] = c_pmt_create_pmat(nx, 1);
    self->b[5] = c_pmt_create_pmat(nx, 1);
    self->b[6] = c_pmt_create_pmat(nx, 1);
    self->b[7] = c_pmt_create_pmat(nx, 1);
    self->b[8] = c_pmt_create_pmat(nx, 1);
    self->b[9] = c_pmt_create_pmat(nx, 1);
    self->b[10] = c_pmt_create_pmat(nx, 1);
    self->b[11] = c_pmt_create_pmat(nx, 1);
    self->b[12] = c_pmt_create_pmat(nx, 1);
    self->b[13] = c_pmt_create_pmat(nx, 1);
    self->b[14] = c_pmt_create_pmat(nx, 1);
    self->b[15] = c_pmt_create_pmat(nx, 1);
    self->b[16] = c_pmt_create_pmat(nx, 1);
    self->b[17] = c_pmt_create_pmat(nx, 1);
    self->b[18] = c_pmt_create_pmat(nx, 1);
    self->b[19] = c_pmt_create_pmat(nx, 1);
    self->b[20] = c_pmt_create_pmat(nx, 1);
    self->P[0] = c_pmt_create_pmat(nx, nx);
    self->P[1] = c_pmt_create_pmat(nx, nx);
    self->P[2] = c_pmt_create_pmat(nx, nx);
    self->P[3] = c_pmt_create_pmat(nx, nx);
    self->P[4] = c_pmt_create_pmat(nx, nx);
    self->P[5] = c_pmt_create_pmat(nx, nx);
    self->P[6] = c_pmt_create_pmat(nx, nx);
    self->P[7] = c_pmt_create_pmat(nx, nx);
    self->P[8] = c_pmt_create_pmat(nx, nx);
    self->P[9] = c_pmt_create_pmat(nx, nx);
    self->P[10] = c_pmt_create_pmat(nx, nx);
    self->P[11] = c_pmt_create_pmat(nx, nx);
    self->P[12] = c_pmt_create_pmat(nx, nx);
    self->P[13] = c_pmt_create_pmat(nx, nx);
    self->P[14] = c_pmt_create_pmat(nx, nx);
    self->P[15] = c_pmt_create_pmat(nx, nx);
    self->P[16] = c_pmt_create_pmat(nx, nx);
    self->P[17] = c_pmt_create_pmat(nx, nx);
    self->P[18] = c_pmt_create_pmat(nx, nx);
    self->P[19] = c_pmt_create_pmat(nx, nx);
    self->P[20] = c_pmt_create_pmat(nx, nx);
    self->L[0] = c_pmt_create_pmat(nu, nu);
    self->L[1] = c_pmt_create_pmat(nu, nu);
    self->L[2] = c_pmt_create_pmat(nu, nu);
    self->L[3] = c_pmt_create_pmat(nu, nu);
    self->L[4] = c_pmt_create_pmat(nu, nu);
    self->L[5] = c_pmt_create_pmat(nu, nu);
    self->L[6] = c_pmt_create_pmat(nu, nu);
    self->L[7] = c_pmt_create_pmat(nu, nu);
    self->L[8] = c_pmt_create_pmat(nu, nu);
    self->L[9] = c_pmt_create_pmat(nu, nu);
    self->L[10] = c_pmt_create_pmat(nu, nu);
    self->L[11] = c_pmt_create_pmat(nu, nu);
    self->L[12] = c_pmt_create_pmat(nu, nu);
    self->L[13] = c_pmt_create_pmat(nu, nu);
    self->L[14] = c_pmt_create_pmat(nu, nu);
    self->L[15] = c_pmt_create_pmat(nu, nu);
    self->L[16] = c_pmt_create_pmat(nu, nu);
    self->L[17] = c_pmt_create_pmat(nu, nu);
    self->L[18] = c_pmt_create_pmat(nu, nu);
    self->L[19] = c_pmt_create_pmat(nu, nu);
    self->K[0] = c_pmt_create_pmat(nu, nx);
    self->K[1] = c_pmt_create_pmat(nu, nx);
    self->K[2] = c_pmt_create_pmat(nu, nx);
    self->K[3] = c_pmt_create_pmat(nu, nx);
    self->K[4] = c_pmt_create_pmat(nu, nx);
    self->K[5] = c_pmt_create_pmat(nu, nx);
    self->K[6] = c_pmt_create_pmat(nu, nx);
    self->K[7] = c_pmt_create_pmat(nu, nx);
    self->K[8] = c_pmt_create_pmat(nu, nx);
    self->K[9] = c_pmt_create_pmat(nu, nx);
    self->K[10] = c_pmt_create_pmat(nu, nx);
    self->K[11] = c_pmt_create_pmat(nu, nx);
    self->K[12] = c_pmt_create_pmat(nu, nx);
    self->K[13] = c_pmt_create_pmat(nu, nx);
    self->K[14] = c_pmt_create_pmat(nu, nx);
    self->K[15] = c_pmt_create_pmat(nu, nx);
    self->K[16] = c_pmt_create_pmat(nu, nx);
    self->K[17] = c_pmt_create_pmat(nu, nx);
    self->K[18] = c_pmt_create_pmat(nu, nx);
    self->K[19] = c_pmt_create_pmat(nu, nx);
    self->Hux[0] = c_pmt_create_pmat(nu, nx);
    self->Hux[1] = c_pmt_create_pmat(nu, nx);
    self->Hux[2] = c_pmt_create_pmat(nu, nx);
    self->Hux[3] = c_pmt_create_pmat(nu, nx);
    self->Hux[4] = c_pmt_create_pmat(nu, nx);
    self->Hux[5] = c_pmt_create_pmat(nu, nx);
    self->Hux[6] = c_pmt_create_pmat(nu, nx);
    self->Hux[7] = c_pmt_create_pmat(nu, nx);
    self->Hux[8] = c_pmt_create_pmat(nu, nx);
    self->Hux[9] = c_pmt_create_pmat(nu, nx);
    self->Hux[10] = c_pmt_create_pmat(nu, nx);
    self->Hux[11] = c_pmt_create_pmat(nu, nx);
    self->Hux[12] = c_pmt_create_pmat(nu, nx);
    self->Hux[13] = c_pmt_create_pmat(nu, nx);
    self->Hux[14] = c_pmt_create_pmat(nu, nx);
    self->Hux[15] = c_pmt_create_pmat(nu, nx);
    self->Hux[16] = c_pmt_create_pmat(nu, nx);
    self->Hux[17] = c_pmt_create_pmat(nu, nx);
    self->Hux[18] = c_pmt_create_pmat(nu, nx);
    self->Hux[19] = c_pmt_create_pmat(nu, nx);
    self->kk[0] = c_pmt_create_pmat(nu, 1);
    self->kk[1] = c_pmt_create_pmat(nu, 1);
    self->kk[2] = c_pmt_create_pmat(nu, 1);
    self->kk[3] = c_pmt_create_pmat(nu, 1);
    self->kk[4] = c_pmt_create_pmat(nu, 1);
    self->kk[5] = c_pmt_create_pmat(nu, 1);
    self->kk[6] = c_pmt_create_pmat(nu, 1);
    self->kk[7] = c_pmt_create_pmat(nu, 1);
    self->kk[8] = c_pmt_create_pmat(nu, 1);
    self->kk[9] = c_pmt_create_pmat(nu, 1);
    self->kk[10] = c_pmt_create_pmat(nu, 1);
    self->kk[11] = c_pmt_create_pmat(nu, 1);
    self->kk[12] = c_pmt_create_pmat(nu, 1);
    self->kk[13] = c_pmt_create_pmat(nu, 1);
    self->kk[14] = c_pmt_create_pmat(nu, 1);
    self->kk[15] = c_pmt_create_pmat(nu, 1);
    self->kk[16] = c_pmt_create_pmat(nu, 1);
    self->kk[17] = c_pmt_create_pmat(nu, 1);
    self->kk[18] = c_pmt_create_pmat(nu, 1);
    self->kk[19] = c_pmt_create_pmat(nu, 1);
    self->dx[0] = c_pmt_create_pmat(nx, 1);
    self->dx[1] = c_pmt_create_pmat(nx, 1);
    self->dx[2] = c_pmt_create_pmat(nx, 1);
    self->dx[3] = c_pmt_create_pmat(nx, 1);
    self->dx[4] = c_pmt_create_pmat(nx, 1);
    self->dx[5] = c_pmt_create_pmat(nx, 1);
    self->dx[6] = c_pmt_create_pmat(nx, 1);
    self->dx[7] = c_pmt_create_pmat(nx, 1);
    self->dx[8] = c_pmt_create_pmat(nx, 1);
    self->dx[9] = c_pmt_create_pmat(nx, 1);
    self->dx[10] = c_pmt_create_pmat(nx, 1);
    self->dx[11] = c_pmt_create_pmat(nx, 1);
    self->dx[12] = c_pmt_create_pmat(nx, 1);
    self->dx[13] = c_pmt_create_pmat(nx, 1);
    self->dx[14] = c_pmt_create_pmat(nx, 1);
    self->dx[15] = c_pmt_create_pmat(nx, 1);
    self->dx[16] = c_pmt_create_pmat(nx, 1);
    self->dx[17] = c_pmt_create_pmat(nx, 1);
    self->dx[18] = c_pmt_create_pmat(nx, 1);
    self->dx[19] = c_pmt_create_pmat(nx, 1);
    self->dx[20] = c_pmt_create_pmat(nx, 1);
    self->du[0] = c_pmt_create_pmat(nu, 1);
    self->du[1] = c_pmt_create_pmat(nu, 1);
    self->du[2] = c_pmt_create_pmat(nu, 1);
    self->du[3] = c_pmt_create_pmat(nu, 1);
    self->du[4] = c_pmt_create_pmat(nu, 1);
    self->du[5] = c_pmt_create_pmat(nu, 1);
    self->du[6] = c_pmt_create_pmat(nu, 1);
    self->du[7] = c_pmt_create_pmat(nu, 1);
    self->du[8] = c_pmt_create_pmat(nu, 1);
    self->du[9] = c_pmt_create_pmat(nu, 1);
    self->du[10] = c_pmt_create_pmat(nu, 1);
    self->du[11] = c_pmt_create_pmat(nu, 1);
    self->du[12] = c_pmt_create_pmat(nu, 1);
    self->du[13] = c_pmt_create_pmat(nu, 1);
    self->du[14] = c_pmt_create_pmat(nu, 1);
    self->du[15] = c_pmt_create_pmat(nu, 1);
    self->du[16] = c_pmt_create_pmat(nu, 1);
    self->du[17] = c_pmt_create_pmat(nu, 1);
    self->du[18] = c_pmt_create_pmat(nu, 1);
    self->du[19] = c_pmt_create_pmat(nu, 1);
self->x0 = c_pmt_create_pmat(nx, 1);

self->Q = c_pmt_create_pmat(nx, nx);

self->R = c_pmt_create_pmat(nu, nu);

self->QN = c_pmt_create_pmat(nx, nx);

    c_pmt_pmat_set_el(self->Q, 0, 0, 10.0);
    c_pmt_pmat_set_el(self->Q, 1, 1, 10.0);
    c_pmt_pmat_set_el(self->Q, 2, 2, 0.1);
    c_pmt_pmat_set_el(self->Q, 3, 3, 0.1);
    c_pmt_pmat_set_el(self->R, 0, 0, 0.1);
}


void _Z13terminal_costSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * ___pmt_m0 = c_pmt_create_pmat(nu, nu);
    struct pmat * ___pmt_m1 = c_pmt_create_pmat(nu, nx);
    struct pmat * ___pmt_m2 = c_pmt_create_pmat(nx, nu);
    struct pmat * ___pmt_m3 = c_pmt_create_pmat(nx, nx);
    struct pmat * ___pmt_m4 = c_pmt_create_pmat(nx, nx);
    struct pmat * x = c_pmt_create_pmat(nx, 1);
    struct pmat * u = c_pmt_create_pmat(nu, 1);
    struct pmat * xn = c_pmt_create_pmat(nx, 1);
    struct pmat * A = c_pmt_create_pmat(nx, nx);
    struct pmat * B = c_pmt_create_pmat(nx, nu);
    struct pmat * PA = c_pmt_create_pmat(nx, nx);
    struct pmat * L = c_pmt_create_pmat(nu, nu);
    struct pmat * K = c_pmt_create_pmat(nu, nx);
    c_pmt_casadi_rk4(x, u, xn, A, B);
    c_pmt_pmat_copy(self->Q, self->QN);
    for(int it = 0, ___pmt_end_1 = n_dare; it < ___pmt_end_1; it += 1) {
        c_pmt_pmat_fill(PA, 0.0);
        c_pmt_gemm_ab_nn(1.0, self->QN, A, 1.0, PA, PA);
        c_pmt_pmat_copy(self->R, ___pmt_m0);
        c_pmt_pmat_fill(___pmt_m1, 0.0);
        c_pmt_gemm_ab_tn(1.0, B, self->QN, 1.0, ___pmt_m1, ___pmt_m1);
        c_pmt_gemm_ab_nn(1.0, ___pmt_m1, B, 1.0, ___pmt_m0, ___pmt_m0);
        c_pmt_pmat_fill(L, 0.0);
        c_pmt_potrf(___pmt_m0, L);
        c_pmt_pmat_copy(L, ___pmt_m0);
        c_pmt_pmat_fill(K, 0.0);
        c_pmt_gemm_ab_tn(1.0, B, PA, 1.0, K, K);
        c_pmt_potrsm(___pmt_m0, K);
        c_pmt_pmat_scale(-1.0, K);
        c_pmt_pmat_copy(self->Q, self->QN);
        c_pmt_gemm_ab_tn(1.0, A, PA, 1.0, self->QN, self->QN);
        c_pmt_pmat_fill(___pmt_m2, 0.0);
        c_pmt_gemm_ab_tn(1.0, PA, B, 1.0, ___pmt_m2, ___pmt_m2);
        c_pmt_gemm_ab_nn(1.0, ___pmt_m2, K, 1.0, self->QN, self->QN);
        c_pmt_pmat_copy(self->QN, ___pmt_m3);
        c_pmt_pmat_scale(0.5, ___pmt_m3);
        c_pmt_pmat_tran(self->QN, ___pmt_m4);
        c_pmt_gead(0.5, ___pmt_m4, ___pmt_m3);
        c_pmt_pmat_copy(___pmt_m3, self->QN);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z9linearizeSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    for(int k = 0, ___pmt_end_2 = N; k < ___pmt_end_2; k += 1) {
        c_pmt_casadi_rk4(self->xs[k], self->us[k], self->b[k], self->A[k], self->B[k]);
        c_pmt_gead(-1.0, self->xs[k + 1], self->b[k]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z7riccatiSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * ___pmt_m0 = c_pmt_create_pmat(nu, nu);
    struct pmat * PA = c_pmt_create_pmat(nx, nx);
    struct pmat * PB = c_pmt_create_pmat(nx, nu);
    struct pmat * p = c_pmt_create_pmat(nx, 1);
    struct pmat * Pb = c_pmt_create_pmat(nx, 1);
    c_pmt_pmat_copy(self->QN, self->P[N]);
    c_pmt_pmat_fill(p, 0.0);
    c_pmt_gemm_ab_nn(1.0, self->QN, self->xs[N], 1.0, p, p);
    for(int k = (N - 1), ___pmt_end_3 = (-1); k > ___pmt_end_3; k += -1) {
        c_pmt_pmat_fill(PA, 0.0);
        c_pmt_gemm_ab_nn(1.0, self->P[k + 1], self->A[k], 1.0, PA, PA);
        c_pmt_pmat_fill(PB, 0.0);
        c_pmt_gemm_ab_nn(1.0, self->P[k + 1], self->B[k], 1.0, PB, PB);
        c_pmt_pmat_copy(p, Pb);
        c_pmt_gemm_ab_nn(1.0, self->P[k + 1], self->b[k], 1.0, Pb, Pb);
        c_pmt_pmat_fill(self->Hux[k], 0.0);
        c_pmt_gemm_ab_tn(1.0, self->B[k], PA, 1.0, self->Hux[k], self->Hux[k]);
        c_pmt_pmat_copy(self->R, ___pmt_m0);
        c_pmt_gemm_ab_tn(1.0, self->B[k], PB, 1.0, ___pmt_m0, ___pmt_m0);
        c_pmt_pmat_fill(self->L[k], 0.0);
        c_pmt_potrf(___pmt_m0, self->L[k]);
        c_pmt_pmat_copy(self->L[k], ___pmt_m0);
        c_pmt_pmat_copy(self->Hux[k], self->K[k]);
        c_pmt_potrsm(___pmt_m0, self->K[k]);
        c_pmt_pmat_scale(-1.0, self->K[k]);
        c_pmt_pmat_copy(self->L[k], ___pmt_m0);
        c_pmt_pmat_fill(self->kk[k], 0.0);
        c_pmt_gemm_ab_nn(1.0, self->R, self->us[k], 1.0, self->kk[k], self->kk[k]);
        c_pmt_gemm_ab_tn(1.0, self->B[k], Pb, 1.0, self->kk[k], self->kk[k]);
        c_pmt_potrsm(___pmt_m0, self->kk[k]);
        c_pmt_pmat_scale(-1.0, self->kk[k]);
        c_pmt_pmat_copy(self->Q, self->P[k]);
        c_pmt_gemm_ab_tn(1.0, self->A[k], PA, 1.0, self->P[k], self->P[k]);
        c_pmt_gemm_ab_tn(1.0, self->Hux[k], self->K[k], 1.0, self->P[k], self->P[k]);
        c_pmt_pmat_fill(p, 0.0);
        c_pmt_gemm_ab_nn(1.0, self->Q, self->xs[k], 1.0, p, p);
        c_pmt_gemm_ab_tn(1.0, self->A[k], Pb, 1.0, p, p);
        c_pmt_gemm_ab_tn(1.0, self->Hux[k], self->kk[k], 1.0, p, p);
    }

    c_pmt_pmat_copy(self->x0, self->dx[0]);
    c_pmt_gead(-1.0, self->xs[0], self->dx[0]);
    for(int k = 0, ___pmt_end_4 = N; k < ___pmt_end_4; k += 1) {
        c_pmt_pmat_copy(self->kk[k], self->du[k]);
        c_pmt_gemm_ab_nn(1.0, self->K[k], self->dx[k], 1.0, self->du[k], self->du[k]);
        c_pmt_pmat_copy(self->b[k], self->dx[k + 1]);
        c_pmt_gemm_ab_nn(1.0, self->A[k], self->dx[k], 1.0, self->dx[k + 1], self->dx[k + 1]);
        c_pmt_gemm_ab_nn(1.0, self->B[k], self->du[k], 1.0, self->dx[k + 1], self->dx[k + 1]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


double _Z7iterateSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    double step = 0.0;
    self->_Z9linearize(self);
    self->_Z7riccati(self);
    for(int k = 0, ___pmt_end_5 = N; k < ___pmt_end_5; k += 1) {
        step = fmax(step, fabs(c_pmt_pmat_get_el(self->du[k], 0, 0)));
        c_pmt_gead(1.0, self->du[k], self->us[k]);
    }

    for(int k = 0, ___pmt_end_6 = (N + 1); k < ___pmt_end_6; k += 1) {
        for(int i = 0, ___pmt_end_7 = nx; i < ___pmt_end_7; i += 1) {
            step = fmax(step, fabs(c_pmt_pmat_get_el(self->dx[k], i, 0)));
    }

        c_pmt_gead(1.0, self->dx[k], self->xs[k]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return step;
}


void _Z5shiftSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    for(int k = 0, ___pmt_end_8 = (N - 1); k < ___pmt_end_8; k += 1) {
        c_pmt_pmat_copy(self->us[k + 1], self->us[k]);
    }

    for(int k = 0, ___pmt_end_9 = N; k < ___pmt_end_9; k += 1) {
        c_pmt_pmat_copy(self->xs[k + 1], self->xs[k]);
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

    struct SQP sqp___;
    struct SQP * sqp= &sqp___;
    SQP_constructor(sqp); //
    double step = 0.0;
    int iterations = 0;
    c_pmt_pmat_set_el(sqp->x0, 1, 0, 0.4);
    sqp->_Z13terminal_cost(sqp);
    for(int it = 0, ___pmt_end_10 = n_sqp; it < ___pmt_end_10; it += 1) {
        step = sqp->_Z7iterate(sqp);
        iterations = iterations + 1;
        if(((step < tol))) {
            break;
}
    }

    printf("first solve: %i SQP iterations\n\n", iterations);

    struct pmat * xplant = c_pmt_create_pmat(nx, 1);
    struct pmat * A = c_pmt_create_pmat(nx, nx);
    struct pmat * B = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_copy(sqp->x0, xplant);
    for(int t = 0, ___pmt_end_11 = n_mpc; t < ___pmt_end_11; t += 1) {
        c_pmt_pmat_copy(xplant, sqp->x0);
        step = sqp->_Z7iterate(sqp);
        c_pmt_casadi_rk4(xplant, sqp->us[0], xplant, A, B);
        sqp->_Z5shift(sqp);
    }

    printf("closed loop: final angle %f\n\n", c_pmt_pmat_get_el(xplant, 1, 0));

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
