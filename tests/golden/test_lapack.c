#include "stdlib.h"
#include "test_lapack.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;

#include "prometeo.h"
int main() {
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

    struct pmat * C = c_pmt_create_pmat(n, n);
    for(int i = 0; i < 5; i++) {
        c_pmt_pmat_set_el(C, i, i, 2.0);
    }

    for(int i = 0; i < 4; i++) {
        c_pmt_pmat_set_el(C, (i + 1), i, 0.5);
        c_pmt_pmat_set_el(C, i, (i + 1), 0.5);
    }

    struct pmat * D = c_pmt_create_pmat(n, n);int ipiv[5];

    c_pmt_getrf(C, D, ipiv);
    c_pmt_pmat_print(D);
    c_pmt_potrf(C, D);
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
