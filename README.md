This is prometeo, a modeling tool for embedded high-performance computing. It is a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently write scientific computing programs in a high-level language and generate
high-performance self-contained C code that can be easily deployed on embedded devices.

### installation
In order to install prometeo, simply install the Python package running `pip install .`. Additionally,
in order to be able to successfully generate and run C code, you will have to compile and install the 
shared library associated with the C back end running `make shared && sudo make install_shared` from 
`<prometeo_root>/prometeo/cprmt`. Notice that the default installation path is `/opt/prometeo`. Make sure that 
this location is added to your `LD_LIBRARY_PATH` when you want to run the generated code. Since prometeo relies 
on BLASFEO, make sure that you have cloned the submodule (`git submodule init && git submodule update`) and that 
you have compiled and installed BLASFEO: run `make static_library && make shared_library && sudo make install_shared` 
from `<prometeo_root>/external/blasfeo/`. 

Finally, you can run the examples in `<root>/examples` with `pmt <example_name>.py --cgen=<True/False>`, where the `--cgen` flag determines whether the code is executed by the Python intereter or C code is generated compiled and run.

### a simple example

The Python code
```python
from prometeo *

def main() -> None:

    n: int = 10
    A: pmat = pmat(n, n)
    for i in range(10):
        for j in range(10):
            A[i,j] = 1.0

    B: pmat = pmat(n, n)
    for i in range(10):
        B[0,i] = 2.0

    C: pmat = pmat(n, n)

    C = A * B
    pmat_print(C)

```
can be run by the standard Python interpreter (version >3.6 required) and it 
will perform the described linear algebra operations using the command `pmt simple_example.py --cgen=False`. 
At the same time, the code can be parsed by prometeo and its abstract syntax tree (AST) analyzed in order
to generate the following high-performance C code:
```c
#include "stdlib.h"
#include "simple_example.h"

#include "prometeo.h"


void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void *___c_prmt_8_heap_head; 
void *___c_prmt_64_heap_head; 
void main() {
    ___c_prmt_8_heap = malloc(10000); 
    ___c_prmt_8_heap_head = ___c_prmt_8_heap;
    char *pmem_ptr = (char *)___c_prmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_prmt_8_heap = pmem_ptr;
    ___c_prmt_64_heap = malloc(1000000);
    ___c_prmt_64_heap_head = ___c_prmt_64_heap;
    pmem_ptr = (char *)___c_prmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_prmt_64_heap = pmem_ptr;

    int n = 10;
    struct pmat * A = c_pmt_create_pmat(n, n);
    for(int i = 0; i < 10; i++) {
        for(int j = 0; j < 10; j++) {
            c_pmt_pmat_set_el(A, i, j, 1.0);
    }

    }

    struct pmat * B = c_pmt_create_pmat(n, n);
    for(int i = 0; i < 10; i++) {
        c_pmt_pmat_set_el(B, 0, i, 2.0);
    }

    struct pmat * C = c_pmt_create_pmat(n, n);
    c_pmt_pmat_fill(C, 0.0);
    c_pmt_gemm_nn(A, B, C, C);
    c_pmt_pmat_print(C);
	free(___c_prmt_8_heap_head);
	free(___c_prmt_64_heap_head);
}
```
which relies on the high-performance linear algebra package BLASFEO. The generated code will be readily compiled and run with when running `pmt simple_example.py --cgen=True`.

### a more advanced example
```python
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2]]
class p_class:
    attr_1: int = 1
    attr_2: float = 3.0
    attr_3: pmat = pmat(10, 10) 

    def method_2(self, A: pmat[2,2], B: pmat[2,2], C: pmat[2,2]) -> None:
        C = A * B
        pmat_print(C)
        return

def function1(A: pmat[2,2], B: pmat[2,2], C: pmat[2,2]) -> None:
    C = A * B
    pmat_print(C)
    attr_3: pmat = pmat(10, 10)
    return

def main() -> None:

    n_list: List = plist(int, 10) 
    n_list[0] = 1

    test_class: p_class = p_class()
    test_class.attr_1 = 2

    j: int = 0
    for i in range(10):
        j = j + 1

    while j > 0:
        j = j - 1

    n: int = 10
    A: pmat = pmat(n, n)
    A[0,2] = -2.0

    for i in range(2):
        A[0,i] = A[0,i]

    pmat_fill(A, 1.0)

    B: pmat = pmat(n, n)
    for i in range(2):
        B[0,i] = A[0,i]
    pmat_fill(B, 2.0)

    C: pmat = pmat(n, n)

    test_class.method_2(A, B, C)

    pmat_list: List = plist(pmat, sizes)
    pmat_list[0] = A

    C = A * B
    pmat_print(C)
    C = A + B
    pmat_print(C)
    C = A - B
    pmat_print(C)

    function1(A, B, C)
    function1(pmat_list[0], B, C)

    pmat_fill(A, 0.0)
    for i in range(10):
        A[i,i] = 1.0

    pmat_print(A)

    a : pvec = pvec(10)
    a[1] = 3.0
    b : pvec = pvec(3)
    b[0] = a[1]
    b[1] = A[0, 2]
    A[0,2] = a[0]

    el : float = 1.0
    el = a[1]
    el = A[1, 1]
    pvec_print(a)
    pvec_print(b)

    c : pvec = pvec(10)
    c = A * a
    pvec_print(c)

    # test LU solve
    ipiv: List = plist(int, 2) 
    fact : pmat = pmat(2, 2)
    M : pmat = pmat(2,2)
    pmt_getrf(M, fact, ipiv)
    res: pvec = pvec(2)
    rhs: pvec = pvec(2)
    rhs[0] = 1.0
    rhs[1] = -3.0
    pmt_getrsv(fact, ipiv, rhs)

    # test Cholesky solve
    M[0,0] = 1.0
    M[0,1] = 0.1
    M[1,0] = 0.1
    M[1,1] = 1.0
    pmt_potrf(M, fact)
    pmt_potrsv(fact, rhs)
```
Similarly, the code above can be run by the standard Python interpreter using the command `pmt dgemm.py --cgen=False` and prometeo can generate compile and run the following high-performance C code using instead `pmt dgemm.py --cgen=True`:
```c
#include "stdlib.h"
#include "dgemm.h"

#include "prometeo.h"
void p_class_init(struct p_class *object){
    object->attr_1 = 1;
    object->attr_2 = 3.0;
    object->attr_3 = c_pmt_create_pmat(10, 10);;
    object->_Z8method_2pmatpmatpmat = &_Z8method_2pmatpmatpmatp_class_impl;
}



void _Z8method_2pmatpmatpmatp_class_impl(p_class *self, struct pmat * A, struct pmat * B, struct pmat * C) {
	void *callee_prmt_8_heap = ___c_prmt_8_heap;
	void *callee_prmt_64_heap = ___c_prmt_64_heap;

    c_pmt_pmat_fill(C, 0.0);
    c_pmt_gemm_nn(A, B, C, C);
    c_pmt_pmat_print(C);	___c_prmt_8_heap = callee_prmt_8_heap;
	___c_prmt_64_heap = callee_prmt_64_heap;

    return;
}


void function1(struct pmat * A, struct pmat * B, struct pmat * C) {
	void *callee_prmt_8_heap = ___c_prmt_8_heap;
	void *callee_prmt_64_heap = ___c_prmt_64_heap;

    c_pmt_pmat_fill(C, 0.0);
    c_pmt_gemm_nn(A, B, C, C);
    c_pmt_pmat_print(C);
    struct pmat * attr_3 = c_pmt_create_pmat(10, 10);	___c_prmt_8_heap = callee_prmt_8_heap;
	___c_prmt_64_heap = callee_prmt_64_heap;

    return;
}


void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void *___c_prmt_8_heap_head; 
void *___c_prmt_64_heap_head; 
void main() {
    ___c_prmt_8_heap = malloc(10000); 
    ___c_prmt_8_heap_head = ___c_prmt_8_heap;
    char *pmem_ptr = (char *)___c_prmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_prmt_8_heap = pmem_ptr;
    ___c_prmt_64_heap = malloc(1000000);
    ___c_prmt_64_heap_head = ___c_prmt_64_heap;
    pmem_ptr = (char *)___c_prmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_prmt_64_heap = pmem_ptr;
int n_list[10];

    n_list[0] = 1;
    struct p_class test_class___;
    struct p_class * test_class= &test_class___;
    p_class_init(test_class); //
    test_class->attr_1 = 2;
    int j = 0;
    for(int i = 0; i < 10; i++) {
        j = j + 1;
    }

    while(j > 0) {
        j = j - 1;
    }

    int n = 10;
    struct pmat * A = c_pmt_create_pmat(n, n);
    c_pmt_pmat_set_el(A, 0, 2, -2.0);
    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(A, 0, i, c_pmt_pmat_get_el(A, 0, i));
    }

    c_pmt_pmat_fill(A, 1.0);
    struct pmat * B = c_pmt_create_pmat(n, n);
    for(int i = 0; i < 2; i++) {
        c_pmt_pmat_set_el(B, 0, i, c_pmt_pmat_get_el(A, 0, i));
    }

    c_pmt_pmat_fill(B, 2.0);
    struct pmat * C = c_pmt_create_pmat(n, n);
    test_class->_Z8method_2pmatpmatpmat(test_class, A, B, C);struct pmat * pmat_list[3];

    pmat_list[0] = c_pmt_create_pmat(2, 2);
    pmat_list[1] = c_pmt_create_pmat(2, 2);
    pmat_list[2] = c_pmt_create_pmat(2, 2);
    pmat_list[0] = A;
    c_pmt_pmat_fill(C, 0.0);
    c_pmt_gemm_nn(A, B, C, C);
    c_pmt_pmat_print(C);
    c_pmt_pmat_copy(B, C);
    c_pmt_gead(1.0, A, C);
    c_pmt_pmat_print(C);
    c_pmt_pmat_copy(A, C);
    c_pmt_gead(-1.0, B, C);
    c_pmt_pmat_print(C);
    function1(A, B, C);
    function1(pmat_list[0], B, C);
    c_pmt_pmat_fill(A, 0.0);
    for(int i = 0; i < 10; i++) {
        c_pmt_pmat_set_el(A, i, i, 1.0);
    }

    c_pmt_pmat_print(A);
    struct pvec * a = c_pmt_create_pvec(10);
    c_pmt_pvec_set_el(a, 1, 3.0);
    struct pvec * b = c_pmt_create_pvec(3);
    c_pmt_pvec_set_el(b, 0, c_pmt_pvec_get_el(a, 1));
    c_pmt_pmat_set_el(A, 0, 2, c_pmt_pvec_get_el(a, 0));
    double el = 1.0;
    el = c_pmt_pvec_get_el(a, 1);
    el = c_pmt_pmat_get_el(A, 1, 1);
    c_pmt_pvec_print(a);
    c_pmt_pvec_print(b);
    struct pvec * c = c_pmt_create_pvec(10);
    c_pmt_pvec_fill(c, 0.0);
    c_pmt_gemv_n(A, a, c, c);
    c_pmt_pvec_print(c);int ipiv[2];

    struct pmat * fact = c_pmt_create_pmat(2, 2);
    struct pmat * M = c_pmt_create_pmat(2, 2);
    c_pmt_getrf(M, fact, ipiv);
    struct pvec * res = c_pmt_create_pvec(2);
    struct pvec * rhs = c_pmt_create_pvec(2);
    c_pmt_pvec_set_el(rhs, 0, 1.0);
    c_pmt_pvec_set_el(rhs, 1, -3.0);
    c_pmt_getrsv(fact, ipiv, rhs);
    c_pmt_pmat_set_el(M, 0, 0, 1.0);
    c_pmt_pmat_set_el(M, 0, 1, 0.1);
    c_pmt_pmat_set_el(M, 1, 0, 0.1);
    c_pmt_pmat_set_el(M, 1, 1, 1.0);
    c_pmt_potrf(M, fact);
    c_pmt_potrsv(fact, rhs);
	free(___c_prmt_8_heap_head);
	free(___c_prmt_64_heap_head);
}
```
__Disclaimer: prometeo is still at a very preliminary stage and only very few linear algebra operations and Python constructs are supported for the time being.__

