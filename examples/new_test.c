#include "new_test.h"
int n = 10;
struct prmt_mat * A = prmt_mat(n, n);
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        prmt_mat_set_el(A, i, j, (i * n + j));
}
}
struct prmt_mat * B = prmt_mat(n, n);
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        prmt_mat_set_el(B, i, j, (0.0));
}
}
for (int i = 0; i < n; i++) {
    prmt_mat_set_el(B, i, i, (1.0));
}
struct prmt_mat * C = prmt_mat(n, n);
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        prmt_mat_set_el(C, i, j, (0.0));
}
}
int i = 0.0;
while(i < n) {
    i = i + 1;
}
if(i >= 5) {
    i = i * 2;
}
prmt_gemm_nt(A, B, C, C);
print('\n\nB = ');
prmt_print(B);
print('\n\nA = ');
prmt_print(A);
print('\n\nC = ');
prmt_print(C);
