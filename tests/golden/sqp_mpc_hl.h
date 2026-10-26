#include "prometeo.h"
#include "timing.h"
#include "pmt_aux.h"
#ifdef __cplusplus
extern "C" {
#endif

void c_pmt_casadi_rk4(struct pmat *in_0, struct pmat *in_1, struct pmat *out_0, struct pmat *out_1, struct pmat *out_2);
#define nx 4
#define nu 1
#define N 20
#define x_sizes_0_0 nx
#define x_sizes_0_1 1
#define x_sizes_1_0 nx
#define x_sizes_1_1 1
#define x_sizes_2_0 nx
#define x_sizes_2_1 1
#define x_sizes_3_0 nx
#define x_sizes_3_1 1
#define x_sizes_4_0 nx
#define x_sizes_4_1 1
#define x_sizes_5_0 nx
#define x_sizes_5_1 1
#define x_sizes_6_0 nx
#define x_sizes_6_1 1
#define x_sizes_7_0 nx
#define x_sizes_7_1 1
#define x_sizes_8_0 nx
#define x_sizes_8_1 1
#define x_sizes_9_0 nx
#define x_sizes_9_1 1
#define x_sizes_10_0 nx
#define x_sizes_10_1 1
#define x_sizes_11_0 nx
#define x_sizes_11_1 1
#define x_sizes_12_0 nx
#define x_sizes_12_1 1
#define x_sizes_13_0 nx
#define x_sizes_13_1 1
#define x_sizes_14_0 nx
#define x_sizes_14_1 1
#define x_sizes_15_0 nx
#define x_sizes_15_1 1
#define x_sizes_16_0 nx
#define x_sizes_16_1 1
#define x_sizes_17_0 nx
#define x_sizes_17_1 1
#define x_sizes_18_0 nx
#define x_sizes_18_1 1
#define x_sizes_19_0 nx
#define x_sizes_19_1 1
#define x_sizes_20_0 nx
#define x_sizes_20_1 1
#define u_sizes_0_0 nu
#define u_sizes_0_1 1
#define u_sizes_1_0 nu
#define u_sizes_1_1 1
#define u_sizes_2_0 nu
#define u_sizes_2_1 1
#define u_sizes_3_0 nu
#define u_sizes_3_1 1
#define u_sizes_4_0 nu
#define u_sizes_4_1 1
#define u_sizes_5_0 nu
#define u_sizes_5_1 1
#define u_sizes_6_0 nu
#define u_sizes_6_1 1
#define u_sizes_7_0 nu
#define u_sizes_7_1 1
#define u_sizes_8_0 nu
#define u_sizes_8_1 1
#define u_sizes_9_0 nu
#define u_sizes_9_1 1
#define u_sizes_10_0 nu
#define u_sizes_10_1 1
#define u_sizes_11_0 nu
#define u_sizes_11_1 1
#define u_sizes_12_0 nu
#define u_sizes_12_1 1
#define u_sizes_13_0 nu
#define u_sizes_13_1 1
#define u_sizes_14_0 nu
#define u_sizes_14_1 1
#define u_sizes_15_0 nu
#define u_sizes_15_1 1
#define u_sizes_16_0 nu
#define u_sizes_16_1 1
#define u_sizes_17_0 nu
#define u_sizes_17_1 1
#define u_sizes_18_0 nu
#define u_sizes_18_1 1
#define u_sizes_19_0 nu
#define u_sizes_19_1 1
#define A_sizes_0_0 nx
#define A_sizes_0_1 nx
#define A_sizes_1_0 nx
#define A_sizes_1_1 nx
#define A_sizes_2_0 nx
#define A_sizes_2_1 nx
#define A_sizes_3_0 nx
#define A_sizes_3_1 nx
#define A_sizes_4_0 nx
#define A_sizes_4_1 nx
#define A_sizes_5_0 nx
#define A_sizes_5_1 nx
#define A_sizes_6_0 nx
#define A_sizes_6_1 nx
#define A_sizes_7_0 nx
#define A_sizes_7_1 nx
#define A_sizes_8_0 nx
#define A_sizes_8_1 nx
#define A_sizes_9_0 nx
#define A_sizes_9_1 nx
#define A_sizes_10_0 nx
#define A_sizes_10_1 nx
#define A_sizes_11_0 nx
#define A_sizes_11_1 nx
#define A_sizes_12_0 nx
#define A_sizes_12_1 nx
#define A_sizes_13_0 nx
#define A_sizes_13_1 nx
#define A_sizes_14_0 nx
#define A_sizes_14_1 nx
#define A_sizes_15_0 nx
#define A_sizes_15_1 nx
#define A_sizes_16_0 nx
#define A_sizes_16_1 nx
#define A_sizes_17_0 nx
#define A_sizes_17_1 nx
#define A_sizes_18_0 nx
#define A_sizes_18_1 nx
#define A_sizes_19_0 nx
#define A_sizes_19_1 nx
#define B_sizes_0_0 nx
#define B_sizes_0_1 nu
#define B_sizes_1_0 nx
#define B_sizes_1_1 nu
#define B_sizes_2_0 nx
#define B_sizes_2_1 nu
#define B_sizes_3_0 nx
#define B_sizes_3_1 nu
#define B_sizes_4_0 nx
#define B_sizes_4_1 nu
#define B_sizes_5_0 nx
#define B_sizes_5_1 nu
#define B_sizes_6_0 nx
#define B_sizes_6_1 nu
#define B_sizes_7_0 nx
#define B_sizes_7_1 nu
#define B_sizes_8_0 nx
#define B_sizes_8_1 nu
#define B_sizes_9_0 nx
#define B_sizes_9_1 nu
#define B_sizes_10_0 nx
#define B_sizes_10_1 nu
#define B_sizes_11_0 nx
#define B_sizes_11_1 nu
#define B_sizes_12_0 nx
#define B_sizes_12_1 nu
#define B_sizes_13_0 nx
#define B_sizes_13_1 nu
#define B_sizes_14_0 nx
#define B_sizes_14_1 nu
#define B_sizes_15_0 nx
#define B_sizes_15_1 nu
#define B_sizes_16_0 nx
#define B_sizes_16_1 nu
#define B_sizes_17_0 nx
#define B_sizes_17_1 nu
#define B_sizes_18_0 nx
#define B_sizes_18_1 nu
#define B_sizes_19_0 nx
#define B_sizes_19_1 nu
#define b_sizes_0_0 nx
#define b_sizes_0_1 1
#define b_sizes_1_0 nx
#define b_sizes_1_1 1
#define b_sizes_2_0 nx
#define b_sizes_2_1 1
#define b_sizes_3_0 nx
#define b_sizes_3_1 1
#define b_sizes_4_0 nx
#define b_sizes_4_1 1
#define b_sizes_5_0 nx
#define b_sizes_5_1 1
#define b_sizes_6_0 nx
#define b_sizes_6_1 1
#define b_sizes_7_0 nx
#define b_sizes_7_1 1
#define b_sizes_8_0 nx
#define b_sizes_8_1 1
#define b_sizes_9_0 nx
#define b_sizes_9_1 1
#define b_sizes_10_0 nx
#define b_sizes_10_1 1
#define b_sizes_11_0 nx
#define b_sizes_11_1 1
#define b_sizes_12_0 nx
#define b_sizes_12_1 1
#define b_sizes_13_0 nx
#define b_sizes_13_1 1
#define b_sizes_14_0 nx
#define b_sizes_14_1 1
#define b_sizes_15_0 nx
#define b_sizes_15_1 1
#define b_sizes_16_0 nx
#define b_sizes_16_1 1
#define b_sizes_17_0 nx
#define b_sizes_17_1 1
#define b_sizes_18_0 nx
#define b_sizes_18_1 1
#define b_sizes_19_0 nx
#define b_sizes_19_1 1
#define K_sizes_0_0 nu
#define K_sizes_0_1 nx
#define K_sizes_1_0 nu
#define K_sizes_1_1 nx
#define K_sizes_2_0 nu
#define K_sizes_2_1 nx
#define K_sizes_3_0 nu
#define K_sizes_3_1 nx
#define K_sizes_4_0 nu
#define K_sizes_4_1 nx
#define K_sizes_5_0 nu
#define K_sizes_5_1 nx
#define K_sizes_6_0 nu
#define K_sizes_6_1 nx
#define K_sizes_7_0 nu
#define K_sizes_7_1 nx
#define K_sizes_8_0 nu
#define K_sizes_8_1 nx
#define K_sizes_9_0 nu
#define K_sizes_9_1 nx
#define K_sizes_10_0 nu
#define K_sizes_10_1 nx
#define K_sizes_11_0 nu
#define K_sizes_11_1 nx
#define K_sizes_12_0 nu
#define K_sizes_12_1 nx
#define K_sizes_13_0 nu
#define K_sizes_13_1 nx
#define K_sizes_14_0 nu
#define K_sizes_14_1 nx
#define K_sizes_15_0 nu
#define K_sizes_15_1 nx
#define K_sizes_16_0 nu
#define K_sizes_16_1 nx
#define K_sizes_17_0 nu
#define K_sizes_17_1 nx
#define K_sizes_18_0 nu
#define K_sizes_18_1 nx
#define K_sizes_19_0 nu
#define K_sizes_19_1 nx
#define R_sizes_0_0 nu
#define R_sizes_0_1 nu
#define R_sizes_1_0 nu
#define R_sizes_1_1 nu
#define R_sizes_2_0 nu
#define R_sizes_2_1 nu
#define R_sizes_3_0 nu
#define R_sizes_3_1 nu
#define R_sizes_4_0 nu
#define R_sizes_4_1 nu
#define R_sizes_5_0 nu
#define R_sizes_5_1 nu
#define R_sizes_6_0 nu
#define R_sizes_6_1 nu
#define R_sizes_7_0 nu
#define R_sizes_7_1 nu
#define R_sizes_8_0 nu
#define R_sizes_8_1 nu
#define R_sizes_9_0 nu
#define R_sizes_9_1 nu
#define R_sizes_10_0 nu
#define R_sizes_10_1 nu
#define R_sizes_11_0 nu
#define R_sizes_11_1 nu
#define R_sizes_12_0 nu
#define R_sizes_12_1 nu
#define R_sizes_13_0 nu
#define R_sizes_13_1 nu
#define R_sizes_14_0 nu
#define R_sizes_14_1 nu
#define R_sizes_15_0 nu
#define R_sizes_15_1 nu
#define R_sizes_16_0 nu
#define R_sizes_16_1 nu
#define R_sizes_17_0 nu
#define R_sizes_17_1 nu
#define R_sizes_18_0 nu
#define R_sizes_18_1 nu
#define R_sizes_19_0 nu
#define R_sizes_19_1 nu
#define P_sizes_0_0 nx
#define P_sizes_0_1 nx
#define P_sizes_1_0 nx
#define P_sizes_1_1 nx
#define P_sizes_2_0 nx
#define P_sizes_2_1 nx
#define P_sizes_3_0 nx
#define P_sizes_3_1 nx
#define P_sizes_4_0 nx
#define P_sizes_4_1 nx
#define P_sizes_5_0 nx
#define P_sizes_5_1 nx
#define P_sizes_6_0 nx
#define P_sizes_6_1 nx
#define P_sizes_7_0 nx
#define P_sizes_7_1 nx
#define P_sizes_8_0 nx
#define P_sizes_8_1 nx
#define P_sizes_9_0 nx
#define P_sizes_9_1 nx
#define P_sizes_10_0 nx
#define P_sizes_10_1 nx
#define P_sizes_11_0 nx
#define P_sizes_11_1 nx
#define P_sizes_12_0 nx
#define P_sizes_12_1 nx
#define P_sizes_13_0 nx
#define P_sizes_13_1 nx
#define P_sizes_14_0 nx
#define P_sizes_14_1 nx
#define P_sizes_15_0 nx
#define P_sizes_15_1 nx
#define P_sizes_16_0 nx
#define P_sizes_16_1 nx
#define P_sizes_17_0 nx
#define P_sizes_17_1 nx
#define P_sizes_18_0 nx
#define P_sizes_18_1 nx
#define P_sizes_19_0 nx
#define P_sizes_19_1 nx
#define P_sizes_20_0 nx
#define P_sizes_20_1 nx

typedef struct SQP SQP;

struct SQP{
struct pmat * xs[21];
struct pmat * us[20];
struct pmat * A[20];
struct pmat * B[20];
struct pmat * b[20];
struct pmat * dx[21];
struct pmat * du[20];
struct pmat * lb[20];
struct pmat * ub[20];
struct pmat * sl[20];
struct pmat * su[20];
struct pmat * zl[20];
struct pmat * zu[20];
struct pmat * Rt[20];
struct pmat * rt[20];
struct pmat * K[20];
struct pmat * kk[20];
struct pmat * dxn[21];
struct pmat * dun[20];
struct pmat * P[21];
struct pmat * L[20];
struct pmat * Hux[20];
struct pmat * tl[20];
struct pmat * tu[20];
struct pmat * ddu[20];
struct pmat * dsl[20];
struct pmat * dsu[20];
struct pmat * dzl[20];
struct pmat * dzu[20];
struct pmat * x0;
struct pmat * Q;
struct pmat * R;
int ipm_iterations;
void (*_Z8__init__)(SQP *self);
void (*_Z9linearize)(SQP *self);
void (*_Z9lq_factor)(SQP *self);
void (*_Z8lq_solve)(SQP *self);
void (*_Z3rhs)(SQP *self);
void (*_Z10directions)(SQP *self);
double (*_Z8max_stepfloat)(SQP *self, double frac);
void (*_Z3ipm)(SQP *self);
double (*_Z5apply)(SQP *self);
double (*_Z7iterate)(SQP *self);
};

void (_Z8__init__SQP_impl)(SQP *self);
void (_Z9linearizeSQP_impl)(SQP *self);
void (_Z9lq_factorSQP_impl)(SQP *self);
void (_Z8lq_solveSQP_impl)(SQP *self);
void (_Z3rhsSQP_impl)(SQP *self);
void (_Z10directionsSQP_impl)(SQP *self);
double (_Z8max_stepfloatSQP_impl)(SQP *self, double frac);
void (_Z3ipmSQP_impl)(SQP *self);
double (_Z5applySQP_impl)(SQP *self);
double (_Z7iterateSQP_impl)(SQP *self);



int main();
#ifdef __cplusplus
}
#endif


