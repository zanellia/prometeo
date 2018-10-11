#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm_mod.h"

void main(){ 
    int n = 10;
    struct prmt_mat * A = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___prmt_fill(A, 1.0);
    struct prmt_mat * B = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___prmt_fill(B, 2.0);
    struct prmt_mat * C = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___create_print_prmt_mat(C);
    ___c_prmt___prmt_fill(C, 0.0);
    ___c_prmt___prmt_dgemm(A, B, C, C);
    ___c_prmt___create_print_prmt_mat(C);
    ___c_prmt___prmt_copy(B, C);
    ___c_prmt___prmt_dgead(1.0, A, C);
    ___c_prmt___create_print_prmt_mat(C);
    ___c_prmt___prmt_copy(B, C);
    ___c_prmt___prmt_dgead(-1.0, A, C);
    ___c_prmt___create_print_prmt_mat(C);
    ___c_prmt___create_print_prmt_mat(C);
}
