#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"



void function1(struct prmt_mat * A, struct prmt_mat * B, struct prmt_mat * C) {

    ___c_prmt___fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___print(C);
    return ;
}


void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() {
    ___c_prmt_8_heap = malloc(1000); 
    char *mem_ptr = (char *)___c_prmt_8_heap; 
    align_char_to(8, &mem_ptr);
    ___c_prmt_8_heap = mem_ptr;
    ___c_prmt_64_heap = malloc(100000); 
    mem_ptr = (char *)___c_prmt_64_heap; 
    align_char_to(64, &mem_ptr);
    ___c_prmt_64_heap = mem_ptr;

    int j = 0;
    for(int i = 0; i < 10; i++) {
        j = j + 1;
    }

    while(j > 0) {
        j = j - 1;
    }

    int * n_list;
    int n = 10;
    struct prmt_mat * A = ___c_prmt___create_prmt_mat(n, n);
    prmt_mat_set_el(A, 0, 2, 2.0);
    for(int i = 0; i < 2; i++) {
        prmt_mat_set_el(A, 0, i, prmt_mat_get_el(A, 0, i));
    }

    ___c_prmt___fill(A, 1.0);
    struct prmt_mat * B = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___fill(B, 2.0);
    struct prmt_mat * C = ___c_prmt___create_prmt_mat(n, n);
    struct prmt_mat ** pmat_list;
    pmat_list[0] = A;
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
    function1(A, B, C);
}
