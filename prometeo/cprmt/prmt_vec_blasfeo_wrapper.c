#include "prmt_vec_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include <assert.h>
#include <blasfeo_common.h>

struct prmt_vec * ___c_prmt___create_prmt_vec(int m) {	
    // assign current address of global heap to pvec pointer
    struct prmt_vec *pvec = (struct prmt_vec *) ___c_prmt_8_heap;
    void *pvec_address = ___c_prmt_8_heap;
    
    // advance global heap address
    ___c_prmt_8_heap += sizeof(struct prmt_vec);
    
    
    // create (zeroed) blasfeo_dvec and advance global heap
    ___c_prmt___assign_and_advance_blasfeo_dvec(m, &(pvec->bvec));

	return (struct prmt_vec *)(pvec_address);
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
    // align_char_to(64, &mem_ptr);
    // ___c_prmt_heap = mem_ptr;
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
