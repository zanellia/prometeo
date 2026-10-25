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

typedef struct SQP SQP;

struct SQP{
struct pmat * xs[21];
struct pmat * us[20];
struct pmat * A[20];
struct pmat * B[20];
struct pmat * b[20];
struct pmat * K[20];
struct pmat * kk[20];
struct pmat * x0;
struct pmat * Q;
struct pmat * R;
void (*_Z8__init__)(SQP *self);
void (*_Z9linearize)(SQP *self);
void (*_Z7riccati)(SQP *self);
double (*_Z7forward)(SQP *self);
double (*_Z7iterate)(SQP *self);
};

void (_Z8__init__SQP_impl)(SQP *self);
void (_Z9linearizeSQP_impl)(SQP *self);
void (_Z7riccatiSQP_impl)(SQP *self);
double (_Z7forwardSQP_impl)(SQP *self);
double (_Z7iterateSQP_impl)(SQP *self);



int main();
#ifdef __cplusplus
}
#endif


