#include "stdlib.h"
#include "simple_class.h"
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

    return a;
}
void Number_constructor(struct Number *object){
    object->_Z8__init__ = &_Z8__init__Number_impl;
    object->_Z9get_value = &_Z9get_valueNumber_impl;
	object->_Z8__init__(object);

}



void _Z8__init__Number_impl(Number *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->value = 1;
}


int _Z9get_valueNumber_impl(Number *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return self->value;
}
void Simple_class_constructor(struct Simple_class *object){
    object->_Z8__init__ = &_Z8__init__Simple_class_impl;
    object->_Z7method1 = &_Z7method1Simple_class_impl;
    object->_Z7method1int = &_Z7method1intSimple_class_impl;
	object->_Z8__init__(object);

}



void _Z8__init__Simple_class_impl(Simple_class *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    self->a = 1;
    self->number= & self->number___;
    Number_constructor(self->number); //
}


int _Z7method1Simple_class_impl(Simple_class *self) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return self->a;
}


int _Z7method1intSimple_class_impl(Simple_class *self, int b) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    int c = self->a + b;
	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return c;
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

    struct Simple_class S___;
    struct Simple_class * S= &S___;
    Simple_class_constructor(S); //
    int a = 1;
    a = _Z3fooint(a);;
    a = S->_Z7method1int(S, a);;
    a = S->_Z7method1(S);;
    a = S->_Z7method1int(S, S->number->value);;
    a = S->number->_Z9get_value(S->number);;
    a = S->number->value;
    a = S->number->_Z9get_value(S->number);;
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
