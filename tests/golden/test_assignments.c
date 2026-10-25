#include "stdlib.h"
#include "test_assignments.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;
void * ___c_pmt_8_heap_end;
void * ___c_pmt_64_heap_end;

#include "prometeo.h"
int main() {
    prometeo_timer timer0, timer1;
    double total_time, execution_time;
    prometeo_tic(&timer0);
    ___c_pmt_8_heap = malloc(HEAP8_SIZE); 
    ___c_pmt_8_heap_head = ___c_pmt_8_heap;
    ___c_pmt_8_heap_end = (char *) ___c_pmt_8_heap + HEAP8_SIZE;
    char * pmem_ptr = (char *)___c_pmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_pmt_8_heap = pmem_ptr;
    ___c_pmt_64_heap = malloc(HEAP64_SIZE);
    ___c_pmt_64_heap_head = ___c_pmt_64_heap;
    ___c_pmt_64_heap_end = (char *) ___c_pmt_64_heap + HEAP64_SIZE;
    pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    prometeo_tic(&timer1);
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    int int_var = 1;
    printf("int variable declaration:\n%i\n\n", int_var);

    double float_var = 1.0;
    printf("float variable declaration:\n%f\n\n", float_var);

    struct pvec * pvec_var = c_pmt_create_pvec(n);
    printf("pvec variable declaration:\n");

    c_pmt_pvec_print(pvec_var);
    struct pmat * pmat_var = c_pmt_create_pmat(n, n);
    printf("pmat variable declaration:\n");

    c_pmt_pmat_print(pmat_var);
    c_pmt_pvec_set_el(pvec_var, 0, float_var);
    printf("float to pvec:\n");

    c_pmt_pvec_print(pvec_var);
    c_pmt_pvec_set_el(pvec_var, 1, 3.0);
    printf("float (const) to pvec:\n");

    c_pmt_pvec_print(pvec_var);
    c_pmt_pmat_set_el(pmat_var, 0, 1, float_var);
    printf("float to pmat:\n");

    c_pmt_pmat_print(pmat_var);
    c_pmt_pmat_set_el(pmat_var, 1, 1, 2.0);
    printf("float (const) to pmat:\n");

    c_pmt_pmat_print(pmat_var);
    float_var = c_pmt_pvec_get_el(pvec_var, 0);
    printf("pvec to float:\n%f\n\n", float_var);

    float_var = c_pmt_pmat_get_el(pmat_var, 1, 1);
    printf("pmat to float:\n%f\n\n", float_var);

    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(pmat_var, 0,                                             i, c_pmt_pmat_get_el(pmat_var, 0, i));
    }

    c_pmt_pvec_set_el(pvec_var, 0, c_pmt_pvec_get_el(pvec_var, 1));
    c_pmt_pmat_set_el(pmat_var, 0,                                             2, c_pmt_pvec_get_el(pvec_var, 1));
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
