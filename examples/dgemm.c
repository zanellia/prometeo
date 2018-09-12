#include "dgemm.h"
int n = 10;
struct prmt_mat * A = prmt_mat(n, n);
struct prmt_mat * B = prmt_mat(n, n);
struct prmt_mat * C = prmt_mat(n, n);
prmt_fill(C, 0.0);
prmt_dgemm(A, B, C, C);
prmt_fill(C, 0.0);
prmt_dgead(A, B, C, C);
C = A - B;
