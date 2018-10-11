This is prometeo, a modeling tool for embedded high-performance computing. It is a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently write scientific computing programs in a high-level language and generate
high-performance self-contained C code that can be easily deployed on embedded devices.

A simple example. The Python code
```python
from prometeo.linalg import *

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
```
can be run by the standard Python interpreter (version >3.6 required) and it 
will perform the described linear algebra operations. At the same time, the code
can be parsed by prometeo and its abstract syntax tree (AST) analyzed in order
to generate the following high-performance C code:
```c
#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"
#include "dgemm.h"
void *___c_prmt_8_heap; 
void *___c_prmt_64_heap; 
void main() { 
___c_prmt_8_heap = malloc(1000); 
___c_prmt_64_heap = malloc(100000); 

int n = 10;
struct prmt_mat * a = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___fill(a, 1.0);
struct prmt_mat * b = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___fill(b, 2.0);
struct prmt_mat * c = ___c_prmt___create_prmt_mat(n, n);
___c_prmt___print(c);
___c_prmt___fill(c, 0.0);
___c_prmt___dgemm(a, b, c, c);
___c_prmt___print(c);
___c_prmt___copy(b, c);
___c_prmt___dgead(1.0, a, c);
___c_prmt___print(c);
___c_prmt___copy(a, c);
___c_prmt___dgead(-1.0, b, c);
___c_prmt___print(c);
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

