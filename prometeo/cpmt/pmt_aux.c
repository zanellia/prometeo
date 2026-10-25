#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include "pmt_aux.h"
#include "pmt_heap.h"

// abort if the program used more memory than the computed bound
void c_pmt_check_heap(void)
{
    if ((___c_pmt_8_heap_end && (char *) ___c_pmt_8_heap > (char *) ___c_pmt_8_heap_end) ||
            (___c_pmt_64_heap_end && (char *) ___c_pmt_64_heap > (char *) ___c_pmt_64_heap_end)) {
        fprintf(stderr, "prometeo: heap overflow, the program uses more memory than the "
            "computed worst-case bound\n");
        exit(1);
    }
}

int align_char_to(int num, char **c_ptr)
{
    size_t s_ptr = (size_t) *c_ptr;
    s_ptr = (s_ptr + num - 1) / num * num;
    int offset = num - (int) (s_ptr - (size_t)(*c_ptr));
    *c_ptr = (char *) s_ptr;
    return offset;
}

int c_pmt_imin(int a, int b) { return a < b ? a : b; }

int c_pmt_imax(int a, int b) { return a > b ? a : b; }
