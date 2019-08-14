This is prometeo, a modeling tool for embedded high-performance computing. It is a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently write scientific computing programs in a high-level language and generate
high-performance self-contained C code that can be easily deployed on embedded devices.

### installation
In order to install prometeo, simply install the Python package running `pip install .`. Additionally,
in order to be able to successfully generate and run C code, you will have to compile and install the 
shared library associated with the C back end running `make shared & sudo make install_shared` from 
`<prometeo_root>/prometeo/cprmt`. Notice that the default installation path is `/opt/prometeo`. Make sure that 
this location is added to your `LD_LIBRARY_PATH` when you want to run the generated code. Since prometeo relies 
on BLASFEO, make sure that you have cloned the submodule (`git submodule init & git submodule update`) and that 
you have compiled and installed BLASFEO: run `make static_library & make shared_library & sudo make install_shared` 
from `<prometeo_root>/external/blasfeo/`.

### a simple example

The Python code
```python
from prometeo.linalg import *
from prometeo.auxl import *

def main() -> None:

    n: int = 10
    A: pmat = pmat(n, n)
    for i in range(10):
        for j in range(10):
            A[i][j] = 1.0

    B: pmat = pmat(n, n)
    for i in range(10):
        B[0][i] = 2.0

    C: pmat = pmat(n, n)

    C = A * B
    pmat_print(C)

if __name__ == "__main__":
    main()
```
can be run by the standard Python interpreter (version >3.6 required) and it 
will perform the described linear algebra operations. At the same time, the code
can be parsed by prometeo and its abstract syntax tree (AST) analyzed in order
to generate the following high-performance C code:
```c
#include "stdlib.h"
#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "simple_example.h"



void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() {
    ___c_prmt_8_heap = malloc(1000); 
    char *mem_ptr = (char *)___c_prmt_8_heap; 
    align_char_to(8, &mem_ptr);
    ___c_prmt_8_heap = mem_ptr;
    ___c_prmt_64_heap = malloc(100000); 
    mem_ptr = (char *)___c_prmt_64_heap; 
    align_char_to(64, &mem_ptr);
    ___c_prmt_64_heap = mem_ptr;

    int n = 10;
    struct pmat * A = ___c_prmt___create_pmat(n, n);
    for(int i = 0; i < 10; i++) {
        for(int j = 0; j < 10; j++) {
            ___c_prmt___pmat_set_el(A, i, j, 1.0);
    }

    }

    struct pmat * B = ___c_prmt___create_pmat(n, n);
    for(int i = 0; i < 10; i++) {
        ___c_prmt___pmat_set_el(B, 0, i, 2.0);
    }

    struct pmat * C = ___c_prmt___create_pmat(n, n);
    ___c_prmt___pmat_fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___pmat_print(C);
}
```
which relies on the high-performance linear algebra package BLASFEO. The generated code can be
readily compiled
```make
CC = gcc
CFLAGS += -g -fPIC

SRCS += simple_example.c 
CFLAGS+=-I/opt/prometeo/include -I/opt/blasfeo/include
LIBPATH+=-L/opt/prometeo/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o simple_example $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o
```
and run with `./simple_example` in order to carry out the same operations.

### a more advanced example
```python
from prometeo.linalg import *
from prometeo.auxl import *

class p_class:
    attr_1: int = 1
    attr_2: float = 3.0

    def method_2(self, A: pmat, B: pmat, C: pmat) -> None:
        C = A * B
        pmat_print(C)
        return

def function1(A: pmat, B: pmat, C: pmat) -> None:
    C = A * B
    pmat_print(C)
    return

def main() -> None:

    n_list: List[int] = prmt_list(int, 10) 
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
    A[0][2] = 2.0

    for i in range(2):
        A[0][i] = A[0][i]

    B: pmat = pmat(n, n)
    for i in range(2):
        B[0][i] = A[0][i]

    C: pmat = pmat(n, n)

    test_class.method_2(A, B, C)

    pmat_list: List[pmat] = prmt_list(pmat, 10)
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
        A[i][i] = 1.0

    pmat_print(A)

    a : pvec = pvec(10)
    a[1] = 3.0
    b : pvec = pvec(3)
    b[0] = a[1]
    b[1] = A[0][2]

    pvec_print(a)
    pvec_print(b)

    c : pvec = pvec(10)
    c = A * a
    pvec_print(c)


if __name__ == "__main__":
    main()
```
Similarly, the code above can be run by the standard Python interpreter and prometeo can 
generate the following high-performance C code:
```c
#include "stdlib.h"
#include "pmat_blasfeo_wrapper.h"
#include "pvec_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"

void p_class_init(struct p_class *object){
    object->attr_1 = 1;
    object->attr_2 = 3.0;
    object->_Z8method_2pmatpmatpmat = &_Z8method_2pmatpmatpmatp_class_impl;
}



void _Z8method_2pmatpmatpmatp_class_impl(p_class *self, struct pmat * A, struct pmat * B, struct pmat * C) {
    ___c_prmt___pmat_fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___pmat_print(C);
    return ;
}


void function1(struct pmat * A, struct pmat * B, struct pmat * C) {

    ___c_prmt___pmat_fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___pmat_print(C);
    return ;
}


void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() {
    ___c_prmt_8_heap = malloc(1000); 
    char *mem_ptr = (char *)___c_prmt_8_heap; 
    align_char_to(8, &mem_ptr);
    ___c_prmt_8_heap = mem_ptr;
    ___c_prmt_64_heap = malloc(100000); 
    mem_ptr = (char *)___c_prmt_64_heap; 
    align_char_to(64, &mem_ptr);
    ___c_prmt_64_heap = mem_ptr;

    int n_list[10];
    n_list[0] = 1;
    struct p_class test_class___;
    struct p_class * test_class= &test_class___;
    p_class_init(test_class); // = p_class();
    test_class->attr_1 = 2;
    int j = 0;
    for(int i = 0; i < 10; i++) {
        j = j + 1;
    }

    while(j > 0) {
        j = j - 1;
    }

    int n = 10;
    struct pmat * A = ___c_prmt___create_pmat(n, n);
    ___c_prmt___pmat_set_el(A, 0, 2, 2.0);
    for(int i = 0; i < 2; i++) {
        ___c_prmt___pmat_set_el(A, 0, i, ___c_prmt___pmat_get_el(A, 0, i));
    }

    struct pmat * B = ___c_prmt___create_pmat(n, n);
    for(int i = 0; i < 2; i++) {
        ___c_prmt___pmat_set_el(B, 0, i, ___c_prmt___pmat_get_el(A, 0, i));
    }

    struct pmat * C = ___c_prmt___create_pmat(n, n);
    test_class->_Z8method_2pmatpmatpmat(test_class, A, B, C);
    struct pmat * pmat_list[10];
    pmat_list[0] = A;
    ___c_prmt___pmat_fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___pmat_print(C);
    ___c_prmt___pmat_copy(B, C);
    ___c_prmt___dgead(1.0, A, C);
    ___c_prmt___pmat_print(C);
    ___c_prmt___pmat_copy(A, C);
    ___c_prmt___dgead(-1.0, B, C);
    ___c_prmt___pmat_print(C);
    function1(A, B, C);
    function1(pmat_list[0], B, C);
    ___c_prmt___pmat_fill(A, 0.0);
    for(int i = 0; i < 10; i++) {
        ___c_prmt___pmat_set_el(A, i, i, 1.0);
    }

    ___c_prmt___pmat_print(A);
    struct pvec * a = ___c_prmt___create_pvec(10);
    ___c_prmt___pvec_set_el(a, 1, 3.0);
    struct pvec * b = ___c_prmt___create_pvec(3);
    ___c_prmt___pvec_set_el(b, 0, ___c_prmt___pvec_get_el(a, 1));
    ___c_prmt___pvec_set_el(b, 1, ___c_prmt___pmat_get_el(A, 0, 2));
    ___c_prmt___pvec_print(a);
    ___c_prmt___pvec_print(b);
    struct pvec * c = ___c_prmt___create_pvec(10);
    ___c_prmt___pvec_fill(c, 0.0);
    ___c_prmt___dgemv(A, a, c, c);
    ___c_prmt___pvec_print(c);
}
```
which relies on the high-performance linear algebra package BLASFEO. The generated code can be
readily compiled
```make
CC = gcc
CFLAGS += -g -fPIC

SRCS += dgemm.c 
CFLAGS+=-I/opt/prometeo/include -I/opt/blasfeo/include
LIBPATH+=-L/opt/prometeo/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o dgemm $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o
```
and run in order to carry out the same operations.

__Disclaimer: prometeo is still at a very preliminary stage and only very few linear algebra operations and Python constructs are supported for the time being.__

