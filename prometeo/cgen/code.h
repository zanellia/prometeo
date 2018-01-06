typedef struct class_m class_m;

struct class_m{
double field1;
double field2;
};




typedef struct class_n class_n;

struct class_n{
double field1;
double field2;
};




typedef struct p_class p_class;

struct p_class{
int attr_1;
double attr_2;
double (*_Z8method_1class_mclass_n)(p_class *self, class_m arg1, class_n arg2);
double (*_Z8method_1class_m)(p_class *self, class_m arg1);
double (*_Z8method_2class_m)(p_class *self, class_m arg1);
int (*_Z11loop_methodclass_m)(p_class *self, class_m arg1);
};

double (_Z8method_1class_mclass_np_class_impl)(p_class *self, class_m arg1, class_n arg2);
double (_Z8method_1class_mp_class_impl)(p_class *self, class_m arg1);
double (_Z8method_2class_mp_class_impl)(p_class *self, class_m arg1);
int (_Z11loop_methodclass_mp_class_impl)(p_class *self, class_m arg1);

