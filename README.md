This is prometeo, a modeling tool for embedded high-performance computing. It is a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently scientific computing programs in a high-level language and generate
high-performance self-contained C code that can be easily deployed on embedded devices.

A simple example. The Python code
'''python
from prometeo.linalg import *
import sys 

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
'''
can be run from by the standard Python interpreter (version >3.6 required) and it 
will perform the described linear algebra operations. At the same time, the code
can be parsed by prometeo and its abstract syntax tree (AST) analyzed in order
to generate the following high-performance C code:
'''c
#include "prmt_mat_blasfeo_wrapper.h"
#include "prmt_heap.h"
#include "dgemm.h"
#include "dgemm.h"
void *___c_prmt_heap; 
void main() { 
___c_prmt_heap = malloc(10000000); 

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
}
'''
which relies on the high-performance linear algebra package BLASFEO.
