#include "stdlib.h"
#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"

void p_class_init(struct p_class *object){
    object->attr_1 = 1;
    object->attr_2 = 3.0;
    object->_Z8method_2pmatpmatpmat = &_Z8method_2pmatpmatpmatp_class_impl;
}



void _Z8method_2pmatpmatpmatp_class_impl(p_class *self, struct pmat * A, struct pmat * B, struct pmat * C) {
    c_pmt_pmat_fill(C, 0.0);
    c_pmt_dgemm(A, B, C, C);
    c_pmt_pmat_print(C);
    return ;
}


void function1(struct pmat * A, struct pmat * B, struct pmat * C) {

    c_pmt_pmat_fill(C, 0.0);
    c_pmt_dgemm(A, B, C, C);
    c_pmt_pmat_print(C);
    return ;
}


void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() {
    ___c_prmt_8_heap = malloc(1000); 
    char *pmem_ptr = (char *)___c_prmt_8_heap; 
    align_char_to(8, &pmem_ptr);
    ___c_prmt_8_heap = pmem_ptr;
    ___c_prmt_64_heap = malloc(100000); 
    pmem_ptr = (char *)___c_prmt_64_heap; 
    align_char_to(64, &pmem_ptr);
    ___c_prmt_64_heap = pmem_ptr;

    int n_list[10];
    n_list[0] = 1;
    struct p_class test_class___;
    struct p_class * test_class= &test_class___;
    p_class_init(test_class); // = p_class();
    test_class->attr_1 = 2;
    int j = 0;
    for(int i = 0; i < 10; i++) {
        j = j + 1;
    }

    while(j > 0) {
        j = j - 1;
    }

    int n = 10;
    struct pmat * A = c_pmt_create_pmat(n, n);
    c_pmt_pmat_set_el(A, 0, 2, 2.0);
    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(A, 0, i, c_pmt_pmat_get_el(A, 0, i));
    }

    struct pmat * B = c_pmt_create_pmat(n, n);
    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(B, 0, i, c_pmt_pmat_get_el(A, 0, i));
    }

    struct pmat * C = c_pmt_create_pmat(n, n);
    test_class->_Z8method_2pmatpmatpmat(test_class, A, B, C);
    struct pmat * pmat_list[10];
    pmat_list[0] = A;
    c_pmt_pmat_fill(C, 0.0);
    c_pmt_dgemm(A, B, C, C);
    c_pmt_pmat_print(C);
    c_pmt_pmat_copy(B, C);
    c_pmt_dgead(1.0, A, C);
    c_pmt_pmat_print(C);
    c_pmt_pmat_copy(A, C);
    c_pmt_dgead(-1.0, B, C);
    c_pmt_pmat_print(C);
    function1(A, B, C);
    function1(pmat_list[0], B, C);
    c_pmt_pmat_fill(A, 0.0);
    for(int i = 0; i < 10; i++) {
        c_pmt_pmat_set_el(A, i, i, 1.0);
    }

    c_pmt_pmat_print(A);
    struct pvec * a = c_pmt_create_pvec(10);
    c_pmt_pvec_set_el(a, 1, 3.0);
    struct pvec * b = c_pmt_create_pvec(3);
    c_pmt_pvec_set_el(b, 0, c_pmt_pvec_get_el(a, 1));
    c_pmt_pvec_set_el(b, 1, c_pmt_pmat_get_el(A, 0, 2));
    c_pmt_pvec_print(a);
    c_pmt_pvec_print(b);
    struct pvec * c = c_pmt_create_pvec(10);
    c_pmt_pvec_fill(c, 0.0);
    c_pmt_dgemv(A, a, c, c);
    c_pmt_pvec_print(c);
}
