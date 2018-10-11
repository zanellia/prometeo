#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"
#include "dgemm.h"
void main() { 
void *___c_prmt_heap = malloc(100); 

int n = 10;
struct prmt_mat * A = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___fill(A, 1.0);
struct prmt_mat * B = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___fill(B, 2.0);
struct prmt_mat * C = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___print(C);
___c_prmt___fill(C, 0.0);
___c_prmt___dgemm(A, B, C, C);
___c_prmt___print(C);
___c_prmt___copy(B, C);
___c_prmt___dgead(1.0, A, C);
___c_prmt___print(C);
___c_prmt___copy(B, C);
___c_prmt___dgead(-1.0, A, C);
___c_prmt___print(C);
___c_prmt___print(C);
}
