#include "code.h"
void class_m_init(class_m *object){
    object->field1 = 1.0;
    object->field2 = 2.0;
}

void class_n_init(class_n *object){
    object->field1 = 1.0;
    object->field2 = 2.0;
}

void p_class_init(p_class *object){
    object->attr_1 = 1;
    object->_Z8method_1class_mclass_n = &_Z8method_1class_mclass_np_class_impl;
    object->_Z8method_1class_m = &_Z8method_1class_mp_class_impl;
    object->_Z8method_2class_m = &_Z8method_2class_mp_class_impl;
    object->_Z11loop_methodclass_m = &_Z11loop_methodclass_mp_class_impl;
}



double _Z8method_1class_mclass_np_class_impl(p_class *self, class_m arg1, class_n arg2) {
    double a = arg1.field1;
    double b = arg2.field2;
    double c = a * b + b * a * a;
    return c;}


double _Z8method_1class_mp_class_impl(p_class *self, class_m arg1) {
    double a = arg1.field1;
    double b = arg1.field2;
    double c = a * b + b * a * a;
    return c;}


double _Z8method_2class_mp_class_impl(p_class *self, class_m arg1) {
    double c = arg1.field1 * arg1.field1;
    return c;}


int _Z11loop_methodclass_mp_class_impl(p_class *self, class_m arg1) {
    int res = 0;
    double var1 = 0;
    for (int i = 0; i < var1; i++);
        res = res + 1;
    return res;}
