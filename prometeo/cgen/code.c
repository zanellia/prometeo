#include "code.h"
int n = 10 * 1;
prmt_mat A = prmt_mat(n, n);;
int n2 = n * n;
for (int i = 0; i < n2; i++) {
    A[i] = i;
}
prmt_mat B = prmt_mat(n, n);;
for (int i = 0; i < n; i++) {
    B[i * (n + 1)] = 1.0;
}
prmt_mat C = prmt_mat(n, n);;
dgemm_nt(A, B, C, C);
print('\n\nB = ');
B.print();
print('\n\nA = ');
A.print();
print('\n\nC = ');
C.print();
