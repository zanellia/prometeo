#include "prometeo.h"
#include "timing.h"
#include "pmt_aux.h"
#ifdef __cplusplus
extern "C" {
#endif




int _Z3fooint(int a);



typedef struct Number Number;

struct Number{
int value;
void (*_Z8__init__)(Number *self);
int (*_Z9get_value)(Number *self);
};

void (_Z8__init__Number_impl)(Number *self);
int (_Z9get_valueNumber_impl)(Number *self);



typedef struct Simple_class Simple_class;

struct Simple_class{
int a;
struct Number number___;
struct Number * number;
void (*_Z8__init__)(Simple_class *self);
int (*_Z7method1)(Simple_class *self);
int (*_Z7method1int)(Simple_class *self, int b);
};

void (_Z8__init__Simple_class_impl)(Simple_class *self);
int (_Z7method1Simple_class_impl)(Simple_class *self);
int (_Z7method1intSimple_class_impl)(Simple_class *self, int b);



int main();
#ifdef __cplusplus
}
#endif


