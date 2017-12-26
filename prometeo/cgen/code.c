void p_class_init(p_class *object){
    object->attr_1 = 1;
    object->attr_2 = 3.0;
    object->_Z8method_1type_1type_2 = &_Z8method_1type_1type_2_impl;
    object->_Z8method_1type_1 = &_Z8method_1type_1_impl;
    object->_Z8method_2type_1 = &_Z8method_2type_1_impl;
    object->_Z11loop_methodtype_1 = &_Z11loop_methodtype_1_impl;
}


double _Z8method_1type_1type_2_impl(p_class *self, type_1 arg1, type_2 arg2) {
    double a = arg1.field1;
    double b = arg2.field2;
    double copyarg2 = arg2;
    double c = a * b + b * a * a;
    return c;
}


double _Z8method_1type_1_impl(p_class *self, type_1 arg1) {
    double a = arg1.field1;
    double b = arg1.field2;
    double copyarg1 = arg1;
    double c = a * b + b * a * a;
    return c;
}


double _Z8method_2type_1_impl(p_class *self, type_1 arg1) {
    double c = arg1 * arg1;
    return c;
}


int _Z11loop_methodtype_1_impl(p_class *self, type_1 arg1) {
    int res = 0;
    double var1 = 0;
    var1 = self.method_2(arg1);
    for (int i = 0; i < arg1; i++);
        res = res + 1;
    return res;
}
