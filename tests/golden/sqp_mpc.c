#include "stdlib.h"
#include "sqp_mpc.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;
void * ___c_pmt_8_heap_end;
void * ___c_pmt_64_heap_end;

#include "prometeo.h"

double M = 1.0;
double m = 0.1;
double l = 0.8;
double g = 9.81;
double h = 0.05;
int n_sqp = 30;
double tol = 1e-10;
int n_mpc = 30;void _Z8dynamicspmatpmatpmat(struct pmat * x, struct pmat * u, struct pmat * xdot) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    double th = c_pmt_pmat_get_el(x, 1, 0);
    double om = c_pmt_pmat_get_el(x, 3, 0);
    double F = c_pmt_pmat_get_el(u, 0, 0);
    double s = sin(th);
    double c = cos(th);
    double d = M + m - m * c * c;
    c_pmt_pmat_set_el(xdot, 0, 0, c_pmt_pmat_get_el(x, 2, 0));
    c_pmt_pmat_set_el(xdot, 1, 0, om);
    c_pmt_pmat_set_el(xdot, 2, 0, (-m * l * s * om * om + m * g * c * s + F) / d);
    c_pmt_pmat_set_el(xdot, 3, 0, (-m * l * c * s * om * om + F * c + (M + m) * g * s) / (l * d));
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}void _Z9jacobianspmatpmatpmatpmat(struct pmat * x, struct pmat * u, struct pmat * Jx, struct pmat * Ju) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    double th = c_pmt_pmat_get_el(x, 1, 0);
    double om = c_pmt_pmat_get_el(x, 3, 0);
    double F = c_pmt_pmat_get_el(u, 0, 0);
    double s = sin(th);
    double c = cos(th);
    double d = M + m - m * c * c;
    double dd = 2.0 * m * c * s;
    double n1 = -m * l * s * om * om + m * g * c * s + F;
    double dn1 = -m * l * c * om * om + m * g * (c * c - s * s);
    double n2 = -m * l * c * s * om * om + F * c + (M + m) * g * s;
    double dn2 = -m * l * (c * c - s * s) * om * om - F * s + (M + m) * g * c;
    c_pmt_pmat_fill(Jx, 0.0);
    c_pmt_pmat_set_el(Jx, 0, 2, 1.0);
    c_pmt_pmat_set_el(Jx, 1, 3, 1.0);
    c_pmt_pmat_set_el(Jx, 2, 1, (dn1 * d - n1 * dd) / (d * d));
    c_pmt_pmat_set_el(Jx, 2, 3, -2.0 * m * l * s * om / d);
    c_pmt_pmat_set_el(Jx, 3, 1, (dn2 * d - n2 * dd) / (l * d * d));
    c_pmt_pmat_set_el(Jx, 3, 3, -2.0 * m * l * c * s * om / (l * d));
    c_pmt_pmat_fill(Ju, 0.0);
    c_pmt_pmat_set_el(Ju, 2, 0, 1.0 / d);
    c_pmt_pmat_set_el(Ju, 3, 0, c / (l * d));
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}void _Z3rk4pmatpmatpmatpmatpmat(struct pmat * x, struct pmat * u, struct pmat * xnext, struct pmat * A, struct pmat * B) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * xi = c_pmt_create_pmat(nx, 1);
    struct pmat * k = c_pmt_create_pmat(nx, 1);
    struct pmat * Sx = c_pmt_create_pmat(nx, nx);
    struct pmat * Su = c_pmt_create_pmat(nx, nu);
    struct pmat * dkx = c_pmt_create_pmat(nx, nx);
    struct pmat * dku = c_pmt_create_pmat(nx, nu);
    struct pmat * Jx = c_pmt_create_pmat(nx, nx);
    struct pmat * Ju = c_pmt_create_pmat(nx, nu);
    double a = 0.0;
    double w = 1.0;
    c_pmt_pmat_copy(x, xnext);
    c_pmt_pmat_fill(A, 0.0);
    c_pmt_pmat_fill(B, 0.0);
    for(int stage = 0, ___pmt_end_1 = 4; stage < ___pmt_end_1; stage += 1) {
        c_pmt_pmat_copy(x, xi);
        c_pmt_pmat_fill(Sx, 0.0);
        for(int i = 0, ___pmt_end_2 = nx; i < ___pmt_end_2; i += 1) {
            c_pmt_pmat_set_el(Sx, i, i, 1.0);
    }

        c_pmt_pmat_fill(Su, 0.0);
        if(((stage == 0))) {
            a = 0.0;
            w = 1.0;
        } else if (((stage < 3))) {
            a = 0.5;
            w = 2.0;
        } else {
            a = 1.0;
            w = 1.0;
}
        if(((stage > 0))) {
            c_pmt_gead(a * h, k, xi);
            c_pmt_gead(a * h, dkx, Sx);
            c_pmt_gead(a * h, dku, Su);
}
        _Z8dynamicspmatpmatpmat(xi, u, k);
        _Z9jacobianspmatpmatpmatpmat(xi, u, Jx, Ju);
        c_pmt_gemm_ab(1.0, Jx, Sx, 0.0, dkx, dkx);

        c_pmt_pmat_copy(Ju, dku);
        c_pmt_gemm_nn(Jx, Su, dku, dku);
        c_pmt_gead(w * h / 6.0, k, xnext);
        c_pmt_gead(w * h / 6.0, dkx, A);
        c_pmt_gead(w * h / 6.0, dku, B);
    }

    for(int i = 0, ___pmt_end_3 = nx; i < ___pmt_end_3; i += 1) {
        c_pmt_pmat_set_el(A, i, i, c_pmt_pmat_get_el(A, i, i) + 1.0);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}
void SQP_constructor(struct SQP *object){
    object->_Z8__init__ = &_Z8__init__SQP_impl;
    object->_Z9linearize = &_Z9linearizeSQP_impl;
    object->_Z7riccati = &_Z7riccatiSQP_impl;
    object->_Z7forward = &_Z7forwardSQP_impl;
    object->_Z7iterate = &_Z7iterateSQP_impl;
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
self->x0 = c_pmt_create_pmat(nx, 1);

self->Q = c_pmt_create_pmat(nx, nx);

self->R = c_pmt_create_pmat(nu, nu);

    c_pmt_pmat_set_el(self->Q, 0, 0, 10.0);
    c_pmt_pmat_set_el(self->Q, 1, 1, 10.0);
    c_pmt_pmat_set_el(self->Q, 2, 2, 0.1);
    c_pmt_pmat_set_el(self->Q, 3, 3, 0.1);
    c_pmt_pmat_set_el(self->R, 0, 0, 0.1);
}


void _Z9linearizeSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    for(int k = 0, ___pmt_end_4 = N; k < ___pmt_end_4; k += 1) {
        _Z3rk4pmatpmatpmatpmatpmat(self->xs[k], self->us[k], self->b[k], self->A[k], self->B[k]);
        c_pmt_gead(-1.0, self->xs[k + 1], self->b[k]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z7riccatiSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * P = c_pmt_create_pmat(nx, nx);
    struct pmat * p = c_pmt_create_pmat(nx, 1);
    struct pmat * Pn = c_pmt_create_pmat(nx, nx);
    struct pmat * PA = c_pmt_create_pmat(nx, nx);
    struct pmat * PB = c_pmt_create_pmat(nx, nu);
    struct pmat * Pb = c_pmt_create_pmat(nx, 1);
    struct pmat * Huu = c_pmt_create_pmat(nu, nu);
    struct pmat * L = c_pmt_create_pmat(nu, nu);
    struct pmat * Hux = c_pmt_create_pmat(nu, nx);
    struct pmat * hu = c_pmt_create_pmat(nu, 1);
    c_pmt_pmat_copy(self->Q, P);
    c_pmt_gemm_ab(1.0, self->Q, self->xs[N], 0.0, p, p);

    for(int k = (N - 1), ___pmt_end_5 = (-1); k > ___pmt_end_5; k += -1) {
        c_pmt_pmat_copy(p, Pb);
        c_pmt_gemm_nn(P, self->b[k], Pb, Pb);
        c_pmt_gemm_ab(1.0, P, self->B[k], 0.0, PB, PB);

        c_pmt_pmat_copy(self->R, Huu);
        c_pmt_gemm_tn(self->B[k], PB, Huu, Huu);
        c_pmt_gemm_ab(1.0, P, self->A[k], 0.0, PA, PA);

        c_pmt_pmat_fill(Hux, 0.0);
        c_pmt_gemm_tn(self->B[k], PA, Hux, Hux);
        c_pmt_gemm_ab(1.0, self->R, self->us[k], 0.0, hu, hu);

        c_pmt_gemm_tn(self->B[k], Pb, hu, hu);
        c_pmt_potrf(Huu, L);
        c_pmt_pmat_copy(Hux, self->K[k]);
        c_pmt_potrsm(L, self->K[k]);
        c_pmt_pmat_copy(hu, self->kk[k]);
        c_pmt_potrsm(L, self->kk[k]);
        for(int j = 0, ___pmt_end_6 = nx; j < ___pmt_end_6; j += 1) {
            c_pmt_pmat_set_el(self->K[k], 0, j, -c_pmt_pmat_get_el(self->K[k], 0, j));
    }

        c_pmt_pmat_set_el(self->kk[k], 0, 0, -c_pmt_pmat_get_el(self->kk[k], 0, 0));
        c_pmt_gemm_ab(1.0, self->Q, self->xs[k], 0.0, p, p);

        c_pmt_gemm_tn(self->A[k], Pb, p, p);
        c_pmt_gemm_tn(Hux, self->kk[k], p, p);
        c_pmt_pmat_copy(self->Q, Pn);
        c_pmt_gemm_tn(self->A[k], PA, Pn, Pn);
        c_pmt_gemm_tn(Hux, self->K[k], Pn, Pn);
        c_pmt_pmat_copy(Pn, P);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


double _Z7forwardSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * dx = c_pmt_create_pmat(nx, 1);
    struct pmat * du = c_pmt_create_pmat(nu, 1);
    struct pmat * dxn = c_pmt_create_pmat(nx, 1);
    double step = 0.0;
    c_pmt_pmat_copy(self->x0, dx);
    c_pmt_gead(-1.0, self->xs[0], dx);
    for(int k = 0, ___pmt_end_7 = N; k < ___pmt_end_7; k += 1) {
        c_pmt_pmat_copy(self->kk[k], du);
        c_pmt_gemm_nn(self->K[k], dx, du, du);
        c_pmt_gead(1.0, dx, self->xs[k]);
        c_pmt_gead(1.0, du, self->us[k]);
        for(int i = 0, ___pmt_end_8 = nx; i < ___pmt_end_8; i += 1) {
            step = fmax(step, fabs(c_pmt_pmat_get_el(dx, i, 0)));
    }

        step = fmax(step, fabs(c_pmt_pmat_get_el(du, 0, 0)));
        c_pmt_pmat_copy(self->b[k], dxn);
        c_pmt_gemm_nn(self->A[k], dx, dxn, dxn);
        c_pmt_gemm_nn(self->B[k], du, dxn, dxn);
        c_pmt_pmat_copy(dxn, dx);
    }

    c_pmt_gead(1.0, dx, self->xs[N]);
    for(int i = 0, ___pmt_end_9 = nx; i < ___pmt_end_9; i += 1) {
        step = fmax(step, fabs(c_pmt_pmat_get_el(dx, i, 0)));
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return step;
}


double _Z7iterateSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->_Z9linearize(self);
    self->_Z7riccati(self);
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return self->_Z7forward(self);
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
    double u0 = 0.0;
    c_pmt_pmat_set_el(sqp->x0, 1, 0, 0.4);
    for(int it = 0, ___pmt_end_10 = n_sqp; it < ___pmt_end_10; it += 1) {
        step = sqp->_Z7iterate(sqp);
        if(((step < tol))) {
            break;
}
    }

    printf("converged: step %e\n\n", step);

    for(int k = 0, ___pmt_end_11 = N; k < ___pmt_end_11; k += 1) {
        u0 = c_pmt_pmat_get_el(sqp->us[k], 0, 0);
        printf("u = %.10f\n\n", u0);

    }

    struct pmat * xplant = c_pmt_create_pmat(nx, 1);
    struct pmat * xnext = c_pmt_create_pmat(nx, 1);
    struct pmat * Aplant = c_pmt_create_pmat(nx, nx);
    struct pmat * Bplant = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_copy(sqp->x0, xplant);
    for(int t = 0, ___pmt_end_12 = n_mpc; t < ___pmt_end_12; t += 1) {
        c_pmt_pmat_copy(xplant, sqp->x0);
        step = sqp->_Z7iterate(sqp);
        _Z3rk4pmatpmatpmatpmatpmat(xplant, sqp->us[0], xnext, Aplant, Bplant);
        c_pmt_pmat_copy(xnext, xplant);
    }

    printf("closed-loop state after %i steps:\n\n", n_mpc);

    c_pmt_pmat_print(xplant);
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
