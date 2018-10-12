This is prometeo, a modeling tool for embedded high-performance computing. It is a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently write scientific computing programs in a high-level language and generate
high-performance self-contained C code that can be easily deployed on embedded devices.

A simple example. The Python code
```python
from prometeo.linalg import *

def function1(A: prmt_mat, B: prmt_mat, C: prmt_mat) -> None:
    C = A * B
    prmt_print(C)
    return


def main() -> None:
    n: int = 10

    A: prmt_mat = prmt_mat(n, n)
    prmt_fill(A, 1.0)

    B: prmt_mat = prmt_mat(n, n)
    prmt_fill(B, 2.0)

    C: prmt_mat = prmt_mat(n, n)

    prmt_print(C)
    C = A * B
    prmt_print(C)
    C = A + B
    prmt_print(C)
    C = A - B
    prmt_print(C)
    function1(A, B, C)

if __name__ == "__main__":
    # execute only if run as a script
    main()
```
can be run by the standard Python interpreter (version >3.6 required) and it 
will perform the described linear algebra operations. At the same time, the code
can be parsed by prometeo and its abstract syntax tree (AST) analyzed in order
to generate the following high-performance C code:
```c
#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"



void function1(struct prmt_mat * A, struct prmt_mat * B, struct prmt_mat * C) {

    ___c_prmt___fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___print(C);
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

    int n = 10;
    struct prmt_mat * A = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___fill(A, 1.0);
    struct prmt_mat * B = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___fill(B, 2.0);
    struct prmt_mat * C = ___c_prmt___create_prmt_mat(n, n);
    ___c_prmt___print(C);
    ___c_prmt___fill(C, 0.0);
    ___c_prmt___dgemm(A, B, C, C);
    ___c_prmt___print(C);
    ___c_prmt___copy(B, C);
    ___c_prmt___dgead(1.0, A, C);
    ___c_prmt___print(C);
    ___c_prmt___copy(A, C);
    ___c_prmt___dgead(-1.0, B, C);
    ___c_prmt___print(C);
    function1(A, B, C);
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

