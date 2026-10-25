#ifndef PROMETEO_HEAP_H_
#define PROMETEO_HEAP_H_

#ifdef __cplusplus
extern "C" {
#endif

extern void* ___c_pmt_8_heap;
extern void* ___c_pmt_64_heap;
// end of the heaps, set by the generated main(): allocations beyond them abort
extern void* ___c_pmt_8_heap_end;
extern void* ___c_pmt_64_heap_end;

#ifdef __cplusplus
}
#endif

#endif // PROMETEO_HEAP_H_
