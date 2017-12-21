void p_class_init(p_class *object){
    object->attr_1 = 1;
    object->attr_2 = 3.0;
    object->method_1 = &method_1_impl;
    object->method_2 = &method_2_impl;
    object->loop_method = &loop_method_impl;
}


double method_1_impl(p_class *self, type_1 arg1, type_2 arg2) {
    double a = arg1.field1;
    double b = arg2.field2;
    double copyarg2 = arg2;
    double c = a * b + b * a * a;
    return c;
}


double method_2_impl(p_class *self, type_1 arg1) {
    double c = arg1 * arg1;
    return c;
}


int loop_method_impl(p_class *self, type_1 arg1) {
    int res = 0;
    for (int i = 0; i < arg1; i++);
        res = res + 1;
    return res;
}
