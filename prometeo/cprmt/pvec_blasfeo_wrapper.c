#include "pvec_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include <assert.h>
#include <blasfeo_common.h>

struct pvec * ___c_prmt___create_pvec(int m) {	
    // assign current address of global heap to pvec pointer
    struct pvec *pvec = (struct pvec *) ___c_prmt_8_heap;
    void *pvec_address = ___c_prmt_8_heap;
    
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct pvec);
    
    
    // create (zeroed) blasfeo_dvec and advance global heap
    ___c_prmt___assign_and_advance_blasfeo_dvec(m, &(pvec->bvec));

	return (struct pvec *)(pvec_address);
}


static int align_char_to(int num, char **c_ptr)
{
    size_t s_ptr = (size_t) *c_ptr;
    s_ptr = (s_ptr + num - 1) / num * num;
    int offset = num - (int) (s_ptr - (size_t)(*c_ptr));
    *c_ptr = (char *) s_ptr;
    return offset;
}

void ___c_prmt___assign_and_advance_blasfeo_dvec(int m, struct blasfeo_dvec **bvec) {
    // assign current address of global heap to blasfeo dvec pointer
    assert((size_t) ___c_prmt_8_heap % 8 == 0 && "pointer not 8-byte aligned!");
    *bvec = (struct blasfeo_dvec *) ___c_prmt_8_heap;
    //
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct blasfeo_dvec);

    // assign current address of global heap to memory in blasfeo dvec
    char *mem_ptr = (char *)___c_prmt_64_heap; 
    align_char_to(64, &mem_ptr);
    ___c_prmt_64_heap = mem_ptr;
    assert((size_t) ___c_prmt_64_heap % 64 == 0 && "dvec not 64-byte aligned!");
    blasfeo_create_dvec(m, *bvec, ___c_prmt_64_heap);

    // advance global heap address
    int memsize = (*bvec)->memsize;
    // make_int_multiple_of(64, memsize);
    ___c_prmt_64_heap += memsize;	

    // zero allocated memory
	int i;
	double *pa = (*bvec)->pa;
    int size = (*bvec)->memsize;
	for(i=0; i<size/8; i++) pa[i] = 0.0;
	char *ca = (char *) pa;
	i *= 8;
	for(; i<size; i++) ca[i] = 0;
	return;
}

// auxiliary
void ___c_prmt___pvec_fill(struct pvec *a, double fill_value) {
    int m = a->bvec->m;

    for(int i = 0; i < m; i++)
        blasfeo_dvecin1(fill_value, a->bvec, i);
}

void ___c_prmt___pvec_set_el(struct pvec *a, int i, double fill_value) {

    blasfeo_dvecin1(fill_value, a->bvec, i);
}

double ___c_prmt___pvec_get_el(struct pvec *a, int i) {

    blasfeo_dvecex1(a->bvec, i);
}

void ___c_prmt___pvec_copy(struct pvec *a, struct pvec *b) {
    int m = a->bvec->m;
    double value;

    for(int i = 0; i < m; i++) {
        value = blasfeo_dvecex1(a->bvec, i);
        blasfeo_dvecin1(value, b->bvec, i);
    }
}

void ___c_prmt___pvec_print(struct pvec *a) {
    int m = a->bvec->m;

    blasfeo_print_dvec(m, a->bvec, 0);
}
