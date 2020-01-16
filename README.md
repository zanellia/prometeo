This is prometeo, a modeling tool for embedded high-performance computing. prometeo provides a 
domain specific language (DSL) based on a subset of the Python language that allows 
one to conveniently write scientific computing programs in a high-level language (Python itself) that can be transpiled
to high-performance self-contained C code easily deployable on embedded devices.

### installation
- Run `git submodule update --init` to clone the submodules.
- Run `make install_shared` from `<prometeo_root>/prometeo/cpmt` to compile and install the shared library associated with the C backend. Notice that the default installation path is `<prometeo_root>/prometeo/cpmt/install`.
- You need Python 3.7. or later.
- Optional: to keep things clean you can setup a virtual environment with `virtualenv --python=<path_to_python3.7 <path_to_new_virtualenv>`.
- Run `pip install -e .` from `<prometeo_root>` to install the Python package.

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

### a more advanced example (Riccati factorization)
```python
from prometeo import *

sizes: dimv = [[2,2], [2,2], [2,2], [2,2], [2,2]]
nx: dims  = 2
nxu: dims = 4
nu: dims  = 2
N:  dims  = 5

class qp_data:
    A: List = plist(pmat, sizes)
    B: List = plist(pmat, sizes)
    Q: List = plist(pmat, sizes)
    R: List = plist(pmat, sizes)
    P: List = plist(pmat, sizes)

    fact: List = plist(pmat, sizes)

    def factorize(self) -> None:
        M: pmat = pmat(nxu, nxu)
        Mu: pmat = pmat(nu, nu)
        Mxut: pmat = pmat(nu, nxu)
        Mxx: pmat = pmat(nx, nx)
        Mxu: pmat = pmat(nxu, nu)
        Lu: pmat = pmat(nu, nu)
        Q: pmat = pmat(nx, nx)
        R: pmat = pmat(nu, nu)
        BA: pmat = pmat(nx, nxu)
        BAtP: pmat = pmat(nxu, nx)
        pmat_copy(self.Q[N-1], self.P[N-1])

        for i in range(1, N):
            pmat_hcat(self.B[N-i], self.A[N-i], BA)
            pmt_gemm_tn(BA, self.P[N-i], BAtP, BAtP)

            pmat_copy(self.Q[N-i], Q)
            pmat_copy(self.R[N-i], R)
            M[0:nu,0:nu] = R
            M[nu:nu+nx,nu:nu+nx] = Q

            pmt_gemm_nn(BAtP, BA, M, M)
            Mu[0:nu, 0:nu] = M[0:nu, 0:nu]
            pmt_potrf(Mu, Lu)

            Mxut[0:nx, 0:nx] = M[0:nx, nu:nu+nx]
            Mxu[0:nx, 0:nu] = M[nu:nu+nx, 0:nu]

            pmt_potrsm(Lu, Mxut)
            pmt_gemm_nn(Mxu, Mxut, self.P[N-i-1], Mxx)
            pmt_gead(-1.0, self.P[N-i-1], Mxx)
            pmat_copy(Mxx, self.P[N-i-1])
            pmat_print(self.P[N-i-1])

        return

def main() -> None:

    A: pmat = pmat(nx, nx)
    A[0,0] = 0.8
    A[0,1] = 0.1
    A[1,0] = 0.3
    A[1,1] = 0.8

    B: pmat = pmat(nx, nu)
    B[0,0] = 1.0  
    B[0,1] = 0.0
    B[1,0] = 0.0
    B[1,1] = 1.0

    Q: pmat = pmat(nx, nx)
    Q[0,0] = 1.0  
    Q[0,1] = 0.0
    Q[1,0] = 0.0
    Q[1,1] = 1.0

    R: pmat = pmat(nu, nu)
    R[0,0] = 1.0  
    R[0,1] = 0.0
    R[1,0] = 0.0
    R[1,1] = 1.0

    qp : qp_data = qp_data() 

    for i in range(N):
        qp.A[i] = A

    for i in range(N):
        qp.B[i] = B

    for i in range(N):
        qp.Q[i] = Q

    for i in range(N):
        qp.R[i] = R

    qp.factorize()
```
Similarly, the code above can be run by the standard Python interpreter using the command `pmt dgemm.py --cgen=False` and prometeo can generate compile and run the following high-performance C code using instead `pmt dgemm.py --cgen=True`:
```c
#include "stdlib.h"
#include "riccati.h"

#include "prometeo.h"
void qp_data_init(struct qp_data *object){
    object->A[0] = c_pmt_create_pmat(2, 2);
    object->A[1] = c_pmt_create_pmat(2, 2);
    object->A[2] = c_pmt_create_pmat(2, 2);
    object->A[3] = c_pmt_create_pmat(2, 2);
    object->A[4] = c_pmt_create_pmat(2, 2);
    object->B[0] = c_pmt_create_pmat(2, 2);
    object->B[1] = c_pmt_create_pmat(2, 2);
    object->B[2] = c_pmt_create_pmat(2, 2);
    object->B[3] = c_pmt_create_pmat(2, 2);
    object->B[4] = c_pmt_create_pmat(2, 2);
    object->Q[0] = c_pmt_create_pmat(2, 2);
    object->Q[1] = c_pmt_create_pmat(2, 2);
    object->Q[2] = c_pmt_create_pmat(2, 2);
    object->Q[3] = c_pmt_create_pmat(2, 2);
    object->Q[4] = c_pmt_create_pmat(2, 2);
    object->R[0] = c_pmt_create_pmat(2, 2);
    object->R[1] = c_pmt_create_pmat(2, 2);
    object->R[2] = c_pmt_create_pmat(2, 2);
    object->R[3] = c_pmt_create_pmat(2, 2);
    object->R[4] = c_pmt_create_pmat(2, 2);
    object->P[0] = c_pmt_create_pmat(2, 2);
    object->P[1] = c_pmt_create_pmat(2, 2);
    object->P[2] = c_pmt_create_pmat(2, 2);
    object->P[3] = c_pmt_create_pmat(2, 2);
    object->P[4] = c_pmt_create_pmat(2, 2);
    object->fact[0] = c_pmt_create_pmat(2, 2);
    object->fact[1] = c_pmt_create_pmat(2, 2);
    object->fact[2] = c_pmt_create_pmat(2, 2);
    object->fact[3] = c_pmt_create_pmat(2, 2);
    object->fact[4] = c_pmt_create_pmat(2, 2);
    object->_Z9factorize = &_Z9factorizeqp_data_impl;
}



void _Z9factorizeqp_data_impl(qp_data *self) {
	void *callee_prmt_8_heap = ___c_prmt_8_heap;
	void *callee_prmt_64_heap = ___c_prmt_64_heap;

    struct pmat * M = c_pmt_create_pmat(nxu, nxu);
    struct pmat * Mu = c_pmt_create_pmat(nu, nu);
    struct pmat * Mxut = c_pmt_create_pmat(nu, nxu);
    struct pmat * Mxx = c_pmt_create_pmat(nx, nx);
    struct pmat * Mxu = c_pmt_create_pmat(nxu, nu);
    struct pmat * Lu = c_pmt_create_pmat(nu, nu);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    struct pmat * BA = c_pmt_create_pmat(nx, nxu);
    struct pmat * BAtP = c_pmt_create_pmat(nxu, nx);
    c_pmt_pmat_copy(self->Q[N - 1], self->P[N - 1]);
    for(int i = 1; i < N; i+=1) {
        c_pmt_pmat_hcat(self->B[N - i], self->A[N - i], BA);
        c_pmt_gemm_tn(BA, self->P[N - i], BAtP, BAtP);
        c_pmt_pmat_print(BAtP);
        c_pmt_pmat_copy(self->Q[N - i], Q);
        c_pmt_pmat_copy(self->R[N - i], R);
        c_pmt_gecp(nu-0, nu-0, R, 0, 0, M, 0, 0);
        c_pmt_gecp((nu + nx)-nu, (nu + nx)-nu, Q, 0, 0, M, nu, nu);
        c_pmt_gemm_nn(BAtP, BA, M, M);
        c_pmt_pmat_print(BAtP);
        c_pmt_pmat_print(BA);
        c_pmt_pmat_print(M);
        c_pmt_gecp(nu-0, nu-0, M, 0, 0, Mu, 0, 0);
        c_pmt_potrf(Mu, Lu);
        c_pmt_gecp(nx-0, (nu + nx)-nu, M, 0, 0, Mxut, nu, nu);
        c_pmt_pmat_print(Mxut);
        c_pmt_gecp(nx-0, nu-0, M, nu, nu, Mxu, 0, 0);
        c_pmt_potrsm(Lu, Mxut);
        c_pmt_gemm_nn(Mxu, Mxut, self->P[N - i - 1], Mxx);
        c_pmt_pmat_print(Mxx);
        c_pmt_gead(-1.0, self->P[N - i - 1], Mxx);
        c_pmt_pmat_copy(Mxx, self->P[N - i - 1]);
    }
	___c_prmt_8_heap = callee_prmt_8_heap;
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

    struct pmat * A = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(A, 0, 0, 0.8);
    c_pmt_pmat_set_el(A, 0, 1, 0.1);
    c_pmt_pmat_set_el(A, 1, 0, 0.3);
    c_pmt_pmat_set_el(A, 1, 1, 0.8);
    struct pmat * B = c_pmt_create_pmat(nx, nu);
    c_pmt_pmat_set_el(B, 0, 0, 1.0);
    c_pmt_pmat_set_el(B, 0, 1, 0.0);
    c_pmt_pmat_set_el(B, 1, 0, 0.0);
    c_pmt_pmat_set_el(B, 1, 1, 1.0);
    struct pmat * Q = c_pmt_create_pmat(nx, nx);
    c_pmt_pmat_set_el(Q, 0, 0, 1.0);
    c_pmt_pmat_set_el(Q, 0, 1, 0.0);
    c_pmt_pmat_set_el(Q, 1, 0, 0.0);
    c_pmt_pmat_set_el(Q, 1, 1, 1.0);
    struct pmat * R = c_pmt_create_pmat(nu, nu);
    c_pmt_pmat_set_el(R, 0, 0, 1.0);
    c_pmt_pmat_set_el(R, 0, 1, 0.0);
    c_pmt_pmat_set_el(R, 1, 0, 0.0);
    c_pmt_pmat_set_el(R, 1, 1, 1.0);
    struct qp_data qp___;
    struct qp_data * qp= &qp___;
    qp_data_init(qp); //
    for(int i = 0; i < N; i++) {
        qp->A[i] = A;
    }

    for(int i = 0; i < N; i++) {
        qp->B[i] = B;
    }

    for(int i = 0; i < N; i++) {
        qp->Q[i] = Q;
    }

    for(int i = 0; i < N; i++) {
        qp->R[i] = R;
    }

    qp->_Z9factorize(qp);
free(___c_prmt_8_heap_head);
free(___c_prmt_64_heap_head);
}
```
__Disclaimer: prometeo is still at a very preliminary stage and only very few linear algebra operations and Python constructs are supported for the time being.__

