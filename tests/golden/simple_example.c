#include "stdlib.h"
#include "simple_example.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;

#include "prometeo.h"
int _Z3fooint(int a) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return a + 1;
}int main() {
    prometeo_timer timer0, timer1;
    double total_time, execution_time;
    prometeo_tic(&timer0);
    ___c_pmt_8_heap = malloc(HEAP8_SIZE); 
    ___c_pmt_8_heap_head = ___c_pmt_8_heap;
    char * pmem_ptr = (char *)___c_pmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_pmt_8_heap = pmem_ptr;
    ___c_pmt_64_heap = malloc(HEAP64_SIZE);
    ___c_pmt_64_heap_head = ___c_pmt_64_heap;
    pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    prometeo_tic(&timer1);
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * A = c_pmt_create_pmat(nv, nv);
    for(int i = 0; i < nv; i++) {
        for(int j = 0; j < nv; j++) {
            c_pmt_pmat_set_el(A, i, j, 1.0);
    }

    }

    struct pmat * B = c_pmt_create_pmat(nv, nv);
    for(int i = 0; i < nv; i++) {
        c_pmt_pmat_set_el(B, 0, i, 2.0);
    }

    struct pmat * D = c_pmt_create_pmat(nv, nv);
    int a = 1;
    int b = 1;
    int c = 1;
    a = (a + b) * c;
    b = _Z3fooint(b);;
    c_pmt_pmat_print(A);
    c_pmt_pmat_print(B);
    blasfeo_dgemm_nn(A->bmat->m, B->bmat->n, A->bmat->n, 1.0, A->bmat, 0, 0, B->bmat, 0, 0, 0.0, D->bmat, 0, 0, D->bmat, 0, 0);

    c_pmt_pmat_print(D);
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

	execution_time = prometeo_toc(&timer1);
	printf("execution time:%fs\n", execution_time);
	free(___c_pmt_8_heap_head);
	free(___c_pmt_64_heap_head);
	total_time = prometeo_toc(&timer0);
	printf("total time:%fs", total_time);
	return 0;
}
