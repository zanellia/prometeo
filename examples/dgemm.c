#include "dgemm.h"
int n = 10;
struct prmt_mat * A = prmt_mat(n, n);
A.fill(1.0);
struct prmt_mat * B = prmt_mat(n, n);
B.fill(2.0);
struct prmt_mat * C = prmt_mat(n, n);
prmt_print(C);
prmt_fill(C, 0.0);
prmt_dgemm(A, B, C, C);
prmt_print(C);
prmt_copy(B, C);
prmt_dgead(1.0, A, C);
prmt_print(C);
prmt_copy(B, C);
prmt_dgead(-1.0, A, C);
prmt_print(C);
