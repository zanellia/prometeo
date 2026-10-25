#include "prometeo.h"
#include "timing.h"
#include "pmt_aux.h"
#ifdef __cplusplus
extern "C" {
#endif

#define sizes_0_0 2
#define sizes_0_1 2
#define sizes_1_0 2
#define sizes_1_1 2
#define sizes_2_0 2
#define sizes_2_1 2
#define sizes_3_0 2
#define sizes_3_1 2
#define sizes_4_0 2
#define sizes_4_1 2
#define nx 2
#define nxu 4
#define nu 2
#define N 5
#define n 10

typedef struct qp_data qp_data;

struct qp_data{
struct pmat * A[5];
struct pmat * B[5];
struct pmat * Q[5];
struct pmat * R[5];
struct pmat * P[5];
struct pmat * fact[5];
void (*_Z8__init__)(qp_data *self);
void (*_Z9factorize)(qp_data *self);
};

void (_Z8__init__qp_data_impl)(qp_data *self);
void (_Z9factorizeqp_data_impl)(qp_data *self);



int main();
#ifdef __cplusplus
}
#endif


