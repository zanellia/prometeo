#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"
#include "dgemm.h"
void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() { 
___c_prmt_8_heap = malloc(1000); 
___c_prmt_64_heap = malloc(1000000); 

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
___c_prmt___copy(A, C);
___c_prmt___dgead(-1.0, B, C);
___c_prmt___print(C);
}
