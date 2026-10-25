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
double u_min = -5.0;
double u_max = 5.0;
int n_sqp = 30;
double tol = 1e-10;
int n_mpc = 30;
int n_ipm = 50;
double ipm_tol = 1e-12;
double sigma = 0.1;
void SQP_constructor(struct SQP *object){
    object->_Z8__init__ = &_Z8__init__SQP_impl;
    object->_Z9linearize = &_Z9linearizeSQP_impl;
    object->_Z2lq = &_Z2lqSQP_impl;
    object->_Z3ipm = &_Z3ipmSQP_impl;
    object->_Z5apply = &_Z5applySQP_impl;
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
    self->lb[0] = c_pmt_create_pmat(nu, 1);
    self->lb[1] = c_pmt_create_pmat(nu, 1);
    self->lb[2] = c_pmt_create_pmat(nu, 1);
    self->lb[3] = c_pmt_create_pmat(nu, 1);
    self->lb[4] = c_pmt_create_pmat(nu, 1);
    self->lb[5] = c_pmt_create_pmat(nu, 1);
    self->lb[6] = c_pmt_create_pmat(nu, 1);
    self->lb[7] = c_pmt_create_pmat(nu, 1);
    self->lb[8] = c_pmt_create_pmat(nu, 1);
    self->lb[9] = c_pmt_create_pmat(nu, 1);
    self->lb[10] = c_pmt_create_pmat(nu, 1);
    self->lb[11] = c_pmt_create_pmat(nu, 1);
    self->lb[12] = c_pmt_create_pmat(nu, 1);
    self->lb[13] = c_pmt_create_pmat(nu, 1);
    self->lb[14] = c_pmt_create_pmat(nu, 1);
    self->lb[15] = c_pmt_create_pmat(nu, 1);
    self->lb[16] = c_pmt_create_pmat(nu, 1);
    self->lb[17] = c_pmt_create_pmat(nu, 1);
    self->lb[18] = c_pmt_create_pmat(nu, 1);
    self->lb[19] = c_pmt_create_pmat(nu, 1);
    self->ub[0] = c_pmt_create_pmat(nu, 1);
    self->ub[1] = c_pmt_create_pmat(nu, 1);
    self->ub[2] = c_pmt_create_pmat(nu, 1);
    self->ub[3] = c_pmt_create_pmat(nu, 1);
    self->ub[4] = c_pmt_create_pmat(nu, 1);
    self->ub[5] = c_pmt_create_pmat(nu, 1);
    self->ub[6] = c_pmt_create_pmat(nu, 1);
    self->ub[7] = c_pmt_create_pmat(nu, 1);
    self->ub[8] = c_pmt_create_pmat(nu, 1);
    self->ub[9] = c_pmt_create_pmat(nu, 1);
    self->ub[10] = c_pmt_create_pmat(nu, 1);
    self->ub[11] = c_pmt_create_pmat(nu, 1);
    self->ub[12] = c_pmt_create_pmat(nu, 1);
    self->ub[13] = c_pmt_create_pmat(nu, 1);
    self->ub[14] = c_pmt_create_pmat(nu, 1);
    self->ub[15] = c_pmt_create_pmat(nu, 1);
    self->ub[16] = c_pmt_create_pmat(nu, 1);
    self->ub[17] = c_pmt_create_pmat(nu, 1);
    self->ub[18] = c_pmt_create_pmat(nu, 1);
    self->ub[19] = c_pmt_create_pmat(nu, 1);
    self->sl[0] = c_pmt_create_pmat(nu, 1);
    self->sl[1] = c_pmt_create_pmat(nu, 1);
    self->sl[2] = c_pmt_create_pmat(nu, 1);
    self->sl[3] = c_pmt_create_pmat(nu, 1);
    self->sl[4] = c_pmt_create_pmat(nu, 1);
    self->sl[5] = c_pmt_create_pmat(nu, 1);
    self->sl[6] = c_pmt_create_pmat(nu, 1);
    self->sl[7] = c_pmt_create_pmat(nu, 1);
    self->sl[8] = c_pmt_create_pmat(nu, 1);
    self->sl[9] = c_pmt_create_pmat(nu, 1);
    self->sl[10] = c_pmt_create_pmat(nu, 1);
    self->sl[11] = c_pmt_create_pmat(nu, 1);
    self->sl[12] = c_pmt_create_pmat(nu, 1);
    self->sl[13] = c_pmt_create_pmat(nu, 1);
    self->sl[14] = c_pmt_create_pmat(nu, 1);
    self->sl[15] = c_pmt_create_pmat(nu, 1);
    self->sl[16] = c_pmt_create_pmat(nu, 1);
    self->sl[17] = c_pmt_create_pmat(nu, 1);
    self->sl[18] = c_pmt_create_pmat(nu, 1);
    self->sl[19] = c_pmt_create_pmat(nu, 1);
    self->su[0] = c_pmt_create_pmat(nu, 1);
    self->su[1] = c_pmt_create_pmat(nu, 1);
    self->su[2] = c_pmt_create_pmat(nu, 1);
    self->su[3] = c_pmt_create_pmat(nu, 1);
    self->su[4] = c_pmt_create_pmat(nu, 1);
    self->su[5] = c_pmt_create_pmat(nu, 1);
    self->su[6] = c_pmt_create_pmat(nu, 1);
    self->su[7] = c_pmt_create_pmat(nu, 1);
    self->su[8] = c_pmt_create_pmat(nu, 1);
    self->su[9] = c_pmt_create_pmat(nu, 1);
    self->su[10] = c_pmt_create_pmat(nu, 1);
    self->su[11] = c_pmt_create_pmat(nu, 1);
    self->su[12] = c_pmt_create_pmat(nu, 1);
    self->su[13] = c_pmt_create_pmat(nu, 1);
    self->su[14] = c_pmt_create_pmat(nu, 1);
    self->su[15] = c_pmt_create_pmat(nu, 1);
    self->su[16] = c_pmt_create_pmat(nu, 1);
    self->su[17] = c_pmt_create_pmat(nu, 1);
    self->su[18] = c_pmt_create_pmat(nu, 1);
    self->su[19] = c_pmt_create_pmat(nu, 1);
    self->zl[0] = c_pmt_create_pmat(nu, 1);
    self->zl[1] = c_pmt_create_pmat(nu, 1);
    self->zl[2] = c_pmt_create_pmat(nu, 1);
    self->zl[3] = c_pmt_create_pmat(nu, 1);
    self->zl[4] = c_pmt_create_pmat(nu, 1);
    self->zl[5] = c_pmt_create_pmat(nu, 1);
    self->zl[6] = c_pmt_create_pmat(nu, 1);
    self->zl[7] = c_pmt_create_pmat(nu, 1);
    self->zl[8] = c_pmt_create_pmat(nu, 1);
    self->zl[9] = c_pmt_create_pmat(nu, 1);
    self->zl[10] = c_pmt_create_pmat(nu, 1);
    self->zl[11] = c_pmt_create_pmat(nu, 1);
    self->zl[12] = c_pmt_create_pmat(nu, 1);
    self->zl[13] = c_pmt_create_pmat(nu, 1);
    self->zl[14] = c_pmt_create_pmat(nu, 1);
    self->zl[15] = c_pmt_create_pmat(nu, 1);
    self->zl[16] = c_pmt_create_pmat(nu, 1);
    self->zl[17] = c_pmt_create_pmat(nu, 1);
    self->zl[18] = c_pmt_create_pmat(nu, 1);
    self->zl[19] = c_pmt_create_pmat(nu, 1);
    self->zu[0] = c_pmt_create_pmat(nu, 1);
    self->zu[1] = c_pmt_create_pmat(nu, 1);
    self->zu[2] = c_pmt_create_pmat(nu, 1);
    self->zu[3] = c_pmt_create_pmat(nu, 1);
    self->zu[4] = c_pmt_create_pmat(nu, 1);
    self->zu[5] = c_pmt_create_pmat(nu, 1);
    self->zu[6] = c_pmt_create_pmat(nu, 1);
    self->zu[7] = c_pmt_create_pmat(nu, 1);
    self->zu[8] = c_pmt_create_pmat(nu, 1);
    self->zu[9] = c_pmt_create_pmat(nu, 1);
    self->zu[10] = c_pmt_create_pmat(nu, 1);
    self->zu[11] = c_pmt_create_pmat(nu, 1);
    self->zu[12] = c_pmt_create_pmat(nu, 1);
    self->zu[13] = c_pmt_create_pmat(nu, 1);
    self->zu[14] = c_pmt_create_pmat(nu, 1);
    self->zu[15] = c_pmt_create_pmat(nu, 1);
    self->zu[16] = c_pmt_create_pmat(nu, 1);
    self->zu[17] = c_pmt_create_pmat(nu, 1);
    self->zu[18] = c_pmt_create_pmat(nu, 1);
    self->zu[19] = c_pmt_create_pmat(nu, 1);
    self->Rt[0] = c_pmt_create_pmat(nu, nu);
    self->Rt[1] = c_pmt_create_pmat(nu, nu);
    self->Rt[2] = c_pmt_create_pmat(nu, nu);
    self->Rt[3] = c_pmt_create_pmat(nu, nu);
    self->Rt[4] = c_pmt_create_pmat(nu, nu);
    self->Rt[5] = c_pmt_create_pmat(nu, nu);
    self->Rt[6] = c_pmt_create_pmat(nu, nu);
    self->Rt[7] = c_pmt_create_pmat(nu, nu);
    self->Rt[8] = c_pmt_create_pmat(nu, nu);
    self->Rt[9] = c_pmt_create_pmat(nu, nu);
    self->Rt[10] = c_pmt_create_pmat(nu, nu);
    self->Rt[11] = c_pmt_create_pmat(nu, nu);
    self->Rt[12] = c_pmt_create_pmat(nu, nu);
    self->Rt[13] = c_pmt_create_pmat(nu, nu);
    self->Rt[14] = c_pmt_create_pmat(nu, nu);
    self->Rt[15] = c_pmt_create_pmat(nu, nu);
    self->Rt[16] = c_pmt_create_pmat(nu, nu);
    self->Rt[17] = c_pmt_create_pmat(nu, nu);
    self->Rt[18] = c_pmt_create_pmat(nu, nu);
    self->Rt[19] = c_pmt_create_pmat(nu, nu);
    self->rt[0] = c_pmt_create_pmat(nu, 1);
    self->rt[1] = c_pmt_create_pmat(nu, 1);
    self->rt[2] = c_pmt_create_pmat(nu, 1);
    self->rt[3] = c_pmt_create_pmat(nu, 1);
    self->rt[4] = c_pmt_create_pmat(nu, 1);
    self->rt[5] = c_pmt_create_pmat(nu, 1);
    self->rt[6] = c_pmt_create_pmat(nu, 1);
    self->rt[7] = c_pmt_create_pmat(nu, 1);
    self->rt[8] = c_pmt_create_pmat(nu, 1);
    self->rt[9] = c_pmt_create_pmat(nu, 1);
    self->rt[10] = c_pmt_create_pmat(nu, 1);
    self->rt[11] = c_pmt_create_pmat(nu, 1);
    self->rt[12] = c_pmt_create_pmat(nu, 1);
    self->rt[13] = c_pmt_create_pmat(nu, 1);
    self->rt[14] = c_pmt_create_pmat(nu, 1);
    self->rt[15] = c_pmt_create_pmat(nu, 1);
    self->rt[16] = c_pmt_create_pmat(nu, 1);
    self->rt[17] = c_pmt_create_pmat(nu, 1);
    self->rt[18] = c_pmt_create_pmat(nu, 1);
    self->rt[19] = c_pmt_create_pmat(nu, 1);
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
    self->dxn[0] = c_pmt_create_pmat(nx, 1);
    self->dxn[1] = c_pmt_create_pmat(nx, 1);
    self->dxn[2] = c_pmt_create_pmat(nx, 1);
    self->dxn[3] = c_pmt_create_pmat(nx, 1);
    self->dxn[4] = c_pmt_create_pmat(nx, 1);
    self->dxn[5] = c_pmt_create_pmat(nx, 1);
    self->dxn[6] = c_pmt_create_pmat(nx, 1);
    self->dxn[7] = c_pmt_create_pmat(nx, 1);
    self->dxn[8] = c_pmt_create_pmat(nx, 1);
    self->dxn[9] = c_pmt_create_pmat(nx, 1);
    self->dxn[10] = c_pmt_create_pmat(nx, 1);
    self->dxn[11] = c_pmt_create_pmat(nx, 1);
    self->dxn[12] = c_pmt_create_pmat(nx, 1);
    self->dxn[13] = c_pmt_create_pmat(nx, 1);
    self->dxn[14] = c_pmt_create_pmat(nx, 1);
    self->dxn[15] = c_pmt_create_pmat(nx, 1);
    self->dxn[16] = c_pmt_create_pmat(nx, 1);
    self->dxn[17] = c_pmt_create_pmat(nx, 1);
    self->dxn[18] = c_pmt_create_pmat(nx, 1);
    self->dxn[19] = c_pmt_create_pmat(nx, 1);
    self->dxn[20] = c_pmt_create_pmat(nx, 1);
    self->dun[0] = c_pmt_create_pmat(nu, 1);
    self->dun[1] = c_pmt_create_pmat(nu, 1);
    self->dun[2] = c_pmt_create_pmat(nu, 1);
    self->dun[3] = c_pmt_create_pmat(nu, 1);
    self->dun[4] = c_pmt_create_pmat(nu, 1);
    self->dun[5] = c_pmt_create_pmat(nu, 1);
    self->dun[6] = c_pmt_create_pmat(nu, 1);
    self->dun[7] = c_pmt_create_pmat(nu, 1);
    self->dun[8] = c_pmt_create_pmat(nu, 1);
    self->dun[9] = c_pmt_create_pmat(nu, 1);
    self->dun[10] = c_pmt_create_pmat(nu, 1);
    self->dun[11] = c_pmt_create_pmat(nu, 1);
    self->dun[12] = c_pmt_create_pmat(nu, 1);
    self->dun[13] = c_pmt_create_pmat(nu, 1);
    self->dun[14] = c_pmt_create_pmat(nu, 1);
    self->dun[15] = c_pmt_create_pmat(nu, 1);
    self->dun[16] = c_pmt_create_pmat(nu, 1);
    self->dun[17] = c_pmt_create_pmat(nu, 1);
    self->dun[18] = c_pmt_create_pmat(nu, 1);
    self->dun[19] = c_pmt_create_pmat(nu, 1);
self->x0 = c_pmt_create_pmat(nx, 1);

self->Q = c_pmt_create_pmat(nx, nx);

self->R = c_pmt_create_pmat(nu, nu);

    self->ipm_iterations = 0;
    c_pmt_pmat_set_el(self->Q, 0, 0, 10.0);
    c_pmt_pmat_set_el(self->Q, 1, 1, 10.0);
    c_pmt_pmat_set_el(self->Q, 2, 2, 0.1);
    c_pmt_pmat_set_el(self->Q, 3, 3, 0.1);
    c_pmt_pmat_set_el(self->R, 0, 0, 0.1);
}


void _Z9linearizeSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    for(int k = 0, ___pmt_end_1 = N; k < ___pmt_end_1; k += 1) {
        c_pmt_casadi_rk4(self->xs[k], self->us[k], self->b[k], self->A[k], self->B[k]);
        c_pmt_gead(-1.0, self->xs[k + 1], self->b[k]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z2lqSQP_impl(SQP *self) {
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

    for(int k = (N - 1), ___pmt_end_2 = (-1); k > ___pmt_end_2; k += -1) {
        c_pmt_pmat_copy(p, Pb);
        c_pmt_gemm_nn(P, self->b[k], Pb, Pb);
        c_pmt_gemm_ab(1.0, P, self->B[k], 0.0, PB, PB);

        c_pmt_pmat_copy(self->Rt[k], Huu);
        c_pmt_gemm_tn(self->B[k], PB, Huu, Huu);
        c_pmt_gemm_ab(1.0, P, self->A[k], 0.0, PA, PA);

        c_pmt_pmat_fill(Hux, 0.0);
        c_pmt_gemm_tn(self->B[k], PA, Hux, Hux);
        c_pmt_pmat_copy(self->rt[k], hu);
        c_pmt_gemm_tn(self->B[k], Pb, hu, hu);
        c_pmt_potrf(Huu, L);
        c_pmt_pmat_copy(Hux, self->K[k]);
        c_pmt_potrsm(L, self->K[k]);
        c_pmt_pmat_copy(hu, self->kk[k]);
        c_pmt_potrsm(L, self->kk[k]);
        for(int i = 0, ___pmt_end_3 = nu; i < ___pmt_end_3; i += 1) {
            for(int j = 0, ___pmt_end_4 = nx; j < ___pmt_end_4; j += 1) {
                c_pmt_pmat_set_el(self->K[k], i, j, -c_pmt_pmat_get_el(self->K[k], i, j));
    }

            c_pmt_pmat_set_el(self->kk[k], i, 0, -c_pmt_pmat_get_el(self->kk[k], i, 0));
    }

        c_pmt_gemm_ab(1.0, self->Q, self->xs[k], 0.0, p, p);

        c_pmt_gemm_tn(self->A[k], Pb, p, p);
        c_pmt_gemm_tn(Hux, self->kk[k], p, p);
        c_pmt_pmat_copy(self->Q, Pn);
        c_pmt_gemm_tn(self->A[k], PA, Pn, Pn);
        c_pmt_gemm_tn(Hux, self->K[k], Pn, Pn);
        c_pmt_pmat_copy(Pn, P);
    }

    c_pmt_pmat_copy(self->x0, self->dxn[0]);
    c_pmt_gead(-1.0, self->xs[0], self->dxn[0]);
    for(int k = 0, ___pmt_end_5 = N; k < ___pmt_end_5; k += 1) {
        c_pmt_pmat_copy(self->kk[k], self->dun[k]);
        c_pmt_gemm_nn(self->K[k], self->dxn[k], self->dun[k], self->dun[k]);
        c_pmt_pmat_copy(self->b[k], self->dxn[k + 1]);
        c_pmt_gemm_nn(self->A[k], self->dxn[k], self->dxn[k + 1], self->dxn[k + 1]);
        c_pmt_gemm_nn(self->B[k], self->dun[k], self->dxn[k + 1], self->dxn[k + 1]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


void _Z3ipmSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    double mu = 0.0;
    double res = 0.0;
    double pairs = 0.0;
    double alpha = 1.0;
    for(int k = 0, ___pmt_end_6 = N; k < ___pmt_end_6; k += 1) {
        for(int i = 0, ___pmt_end_7 = nu; i < ___pmt_end_7; i += 1) {
            c_pmt_pmat_set_el(self->lb[k], i, 0, u_min - c_pmt_pmat_get_el(self->us[k], i, 0));
            c_pmt_pmat_set_el(self->ub[k], i, 0, u_max - c_pmt_pmat_get_el(self->us[k], i, 0));
            c_pmt_pmat_set_el(self->du[k], i, 0, 0.0);
            c_pmt_pmat_set_el(self->sl[k], i, 0, 1.0);
            c_pmt_pmat_set_el(self->su[k], i, 0, 1.0);
            c_pmt_pmat_set_el(self->zl[k], i, 0, 1.0);
            c_pmt_pmat_set_el(self->zu[k], i, 0, 1.0);
    }

    }

    for(int it = 0, ___pmt_end_8 = n_ipm; it < ___pmt_end_8; it += 1) {
        self->ipm_iterations = it;
        mu = 0.0;
        res = 0.0;
        pairs = 0.0;
        for(int k = 0, ___pmt_end_9 = N; k < ___pmt_end_9; k += 1) {
            for(int i = 0, ___pmt_end_10 = nu; i < ___pmt_end_10; i += 1) {
                mu = mu + (c_pmt_pmat_get_el(self->sl[k], i, 0) * c_pmt_pmat_get_el(self->zl[k], i, 0) + c_pmt_pmat_get_el(self->su[k], i, 0) * c_pmt_pmat_get_el(self->zu[k], i, 0));
                pairs = pairs + 2.0;
                res = fmax(res, fabs(c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->lb[k], i, 0) - c_pmt_pmat_get_el(self->sl[k], i, 0)));
                res = fmax(res, fabs(c_pmt_pmat_get_el(self->ub[k], i, 0) - c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->su[k], i, 0)));
    }

    }

        mu = mu / pairs;
        if(((((mu < ipm_tol))) && (((res < ipm_tol))))) {
            break;
}
        for(int k = 0, ___pmt_end_11 = N; k < ___pmt_end_11; k += 1) {
            c_pmt_pmat_copy(self->R, self->Rt[k]);
            c_pmt_gemm_ab(1.0, self->R, self->us[k], 0.0, self->rt[k], self->rt[k]);

            for(int i = 0, ___pmt_end_12 = nu; i < ___pmt_end_12; i += 1) {
                double du = c_pmt_pmat_get_el(self->du[k], i, 0);
                double sl = c_pmt_pmat_get_el(self->sl[k], i, 0);
                double su = c_pmt_pmat_get_el(self->su[k], i, 0);
                double zl = c_pmt_pmat_get_el(self->zl[k], i, 0);
                double zu = c_pmt_pmat_get_el(self->zu[k], i, 0);
                double rl = du - c_pmt_pmat_get_el(self->lb[k], i, 0) - sl;
                double ru = c_pmt_pmat_get_el(self->ub[k], i, 0) - du - su;
                double D = zl / sl + zu / su;
                c_pmt_pmat_set_el(self->Rt[k], i, i, c_pmt_pmat_get_el(self->Rt[k], i, i) + D);
                c_pmt_pmat_set_el(self->rt[k], i, 0, c_pmt_pmat_get_el(self->rt[k], i, 0) + (-D * du - sigma * mu / sl + zl * rl / sl + sigma * mu / su - zu * ru / su));
    }

    }

        self->_Z2lq(self);
        alpha = 1.0;
        for(int k = 0, ___pmt_end_13 = N; k < ___pmt_end_13; k += 1) {
            for(int i = 0, ___pmt_end_14 = nu; i < ___pmt_end_14; i += 1) {
                double ddu = c_pmt_pmat_get_el(self->dun[k], i, 0) - c_pmt_pmat_get_el(self->du[k], i, 0);
                double dsl = ddu + c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->lb[k], i, 0) - c_pmt_pmat_get_el(self->sl[k], i, 0);
                double dsu = c_pmt_pmat_get_el(self->ub[k], i, 0) - c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->su[k], i, 0) - ddu;
                double dzl = (sigma * mu - c_pmt_pmat_get_el(self->zl[k], i, 0) * (c_pmt_pmat_get_el(self->sl[k], i, 0) + dsl)) / c_pmt_pmat_get_el(self->sl[k], i, 0);
                double dzu = (sigma * mu - c_pmt_pmat_get_el(self->zu[k], i, 0) * (c_pmt_pmat_get_el(self->su[k], i, 0) + dsu)) / c_pmt_pmat_get_el(self->su[k], i, 0);
                if(((dsl < 0.0))) {
                    alpha = fmin(alpha, -0.995 * c_pmt_pmat_get_el(self->sl[k], i, 0) / dsl);
}
                if(((dsu < 0.0))) {
                    alpha = fmin(alpha, -0.995 * c_pmt_pmat_get_el(self->su[k], i, 0) / dsu);
}
                if(((dzl < 0.0))) {
                    alpha = fmin(alpha, -0.995 * c_pmt_pmat_get_el(self->zl[k], i, 0) / dzl);
}
                if(((dzu < 0.0))) {
                    alpha = fmin(alpha, -0.995 * c_pmt_pmat_get_el(self->zu[k], i, 0) / dzu);
}
    }

    }

        for(int k = 0, ___pmt_end_15 = N; k < ___pmt_end_15; k += 1) {
            for(int i = 0, ___pmt_end_16 = nu; i < ___pmt_end_16; i += 1) {
                double ddu = c_pmt_pmat_get_el(self->dun[k], i, 0) - c_pmt_pmat_get_el(self->du[k], i, 0);
                double dsl = ddu + c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->lb[k], i, 0) - c_pmt_pmat_get_el(self->sl[k], i, 0);
                double dsu = c_pmt_pmat_get_el(self->ub[k], i, 0) - c_pmt_pmat_get_el(self->du[k], i, 0) - c_pmt_pmat_get_el(self->su[k], i, 0) - ddu;
                double dzl = (sigma * mu - c_pmt_pmat_get_el(self->zl[k], i, 0) * (c_pmt_pmat_get_el(self->sl[k], i, 0) + dsl)) / c_pmt_pmat_get_el(self->sl[k], i, 0);
                double dzu = (sigma * mu - c_pmt_pmat_get_el(self->zu[k], i, 0) * (c_pmt_pmat_get_el(self->su[k], i, 0) + dsu)) / c_pmt_pmat_get_el(self->su[k], i, 0);
                c_pmt_pmat_set_el(self->du[k], i, 0, c_pmt_pmat_get_el(self->du[k], i, 0) + alpha * ddu);
                c_pmt_pmat_set_el(self->sl[k], i, 0, c_pmt_pmat_get_el(self->sl[k], i, 0) + alpha * dsl);
                c_pmt_pmat_set_el(self->su[k], i, 0, c_pmt_pmat_get_el(self->su[k], i, 0) + alpha * dsu);
                c_pmt_pmat_set_el(self->zl[k], i, 0, c_pmt_pmat_get_el(self->zl[k], i, 0) + alpha * dzl);
                c_pmt_pmat_set_el(self->zu[k], i, 0, c_pmt_pmat_get_el(self->zu[k], i, 0) + alpha * dzu);
    }

    }

    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}


double _Z5applySQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    double step = 0.0;
    c_pmt_pmat_copy(self->x0, self->dx[0]);
    c_pmt_gead(-1.0, self->xs[0], self->dx[0]);
    for(int k = 0, ___pmt_end_17 = N; k < ___pmt_end_17; k += 1) {
        c_pmt_pmat_copy(self->b[k], self->dx[k + 1]);
        c_pmt_gemm_nn(self->A[k], self->dx[k], self->dx[k + 1], self->dx[k + 1]);
        c_pmt_gemm_nn(self->B[k], self->du[k], self->dx[k + 1], self->dx[k + 1]);
    }

    for(int k = 0, ___pmt_end_18 = N; k < ___pmt_end_18; k += 1) {
        for(int i = 0, ___pmt_end_19 = nu; i < ___pmt_end_19; i += 1) {
            step = fmax(step, fabs(c_pmt_pmat_get_el(self->du[k], i, 0)));
    }

        c_pmt_gead(1.0, self->du[k], self->us[k]);
    }

    for(int k = 0, ___pmt_end_20 = (N + 1); k < ___pmt_end_20; k += 1) {
        for(int i = 0, ___pmt_end_21 = nx; i < ___pmt_end_21; i += 1) {
            step = fmax(step, fabs(c_pmt_pmat_get_el(self->dx[k], i, 0)));
    }

        c_pmt_gead(1.0, self->dx[k], self->xs[k]);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return step;
}


double _Z7iterateSQP_impl(SQP *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->_Z9linearize(self);
    self->_Z3ipm(self);
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return self->_Z5apply(self);
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
    for(int it = 0, ___pmt_end_22 = n_sqp; it < ___pmt_end_22; it += 1) {
        step = sqp->_Z7iterate(sqp);
        if(((step < tol))) {
            break;
}
    }

    printf("converged: step %e\n\n", step);

    printf("interior-point iterations in the last QP: %i\n\n", sqp->ipm_iterations);

    for(int k = 0, ___pmt_end_23 = N; k < ___pmt_end_23; k += 1) {
        u0 = c_pmt_pmat_get_el(sqp->us[k], 0, 0);
        printf("u = %.10f\n\n", u0);

    }

    struct pmat * xplant = c_pmt_create_pmat(nx, 1);
    struct pmat * xnext = c_pmt_create_pmat(nx, 1);
    struct pmat * Aplant = c_pmt_create_pmat(nx, nx);
    struct pmat * Bplant = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_copy(sqp->x0, xplant);
    for(int t = 0, ___pmt_end_24 = n_mpc; t < ___pmt_end_24; t += 1) {
        c_pmt_pmat_copy(xplant, sqp->x0);
        step = sqp->_Z7iterate(sqp);
        c_pmt_casadi_rk4(xplant, sqp->us[0], xnext, Aplant, Bplant);
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
