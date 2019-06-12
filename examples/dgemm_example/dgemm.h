typedef struct p_class p_class;

struct p_class{
int attr_1;
float attr_2;
void (*_Z8method_2pmatpmatpmat)(p_class *self, struct pmat * A, struct pmat * B, struct pmat * C);
};

void (_Z8method_2pmatpmatpmatp_class_impl)(p_class *self, struct pmat * A, struct pmat * B, struct pmat * C);

