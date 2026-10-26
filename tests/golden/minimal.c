#include "stdlib.h"
#include "minimal.h"
void * ___c_pmt_8_heap;
void * ___c_pmt_64_heap;
void * ___c_pmt_8_heap_head;
void * ___c_pmt_64_heap_head;
void * ___c_pmt_8_heap_end;
void * ___c_pmt_64_heap_end;

#include "prometeo.h"
void _Z3lqrpmatpmatpmatpmatpmatpmat(struct pmat * A, struct pmat * B, struct pmat * Q, struct pmat * R, struct pmat * P, struct pmat * K) {
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pmat * ___pmt_m0 = c_pmt_create_pmat(m, m);
    struct pmat * ___pmt_m1 = c_pmt_create_pmat(m, n);
    struct pmat * ___pmt_m2 = c_pmt_create_pmat(n, n);
    struct pmat * ___pmt_m3 = c_pmt_create_pmat(n, n);
    struct pmat * ___pmt_m4 = c_pmt_create_pmat(n, n);
    struct pmat * L = c_pmt_create_pmat(m, m);
    c_pmt_pmat_copy(Q, P);
    for(int k = 0, ___pmt_end_1 = N; k < ___pmt_end_1; k += 1) {
        c_pmt_pmat_copy(R, ___pmt_m0);
        c_pmt_pmat_fill(___pmt_m1, 0.0);
        c_pmt_gemm_ab_tn(1.0, B, P, 1.0, ___pmt_m1, ___pmt_m1);
        c_pmt_gemm_ab_nn(1.0, ___pmt_m1, B, 1.0, ___pmt_m0, ___pmt_m0);
        c_pmt_pmat_fill(L, 0.0);
        c_pmt_potrf(___pmt_m0, L);
        c_pmt_pmat_copy(L, ___pmt_m0);
        c_pmt_pmat_fill(K, 0.0);
        c_pmt_pmat_fill(___pmt_m1, 0.0);
        c_pmt_gemm_ab_tn(1.0, B, P, 1.0, ___pmt_m1, ___pmt_m1);
        c_pmt_gemm_ab_nn(1.0, ___pmt_m1, A, 1.0, K, K);
        c_pmt_potrsm(___pmt_m0, K);
        c_pmt_pmat_scale(-1.0, K);
        c_pmt_pmat_copy(Q, ___pmt_m2);
        c_pmt_pmat_fill(___pmt_m3, 0.0);
        c_pmt_gemm_ab_tn(1.0, A, P, 1.0, ___pmt_m3, ___pmt_m3);
        c_pmt_pmat_copy(A, ___pmt_m4);
        c_pmt_gemm_ab_nn(1.0, B, K, 1.0, ___pmt_m4, ___pmt_m4);
        c_pmt_gemm_ab_nn(1.0, ___pmt_m3, ___pmt_m4, 1.0, ___pmt_m2, ___pmt_m2);
        c_pmt_pmat_copy(___pmt_m2, P);
        c_pmt_pmat_copy(P, ___pmt_m2);
        c_pmt_pmat_scale(0.5, ___pmt_m2);
        c_pmt_pmat_tran(P, ___pmt_m3);
        c_pmt_gead(0.5, ___pmt_m3, ___pmt_m2);
        c_pmt_pmat_copy(___pmt_m2, P);
    }

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

    return;
}int main() {
    prometeo_timer timer0, timer1;
    double total_time, execution_time;
    prometeo_tic(&timer0);
    ___c_pmt_8_heap = malloc(HEAP8_SIZE); 
    ___c_pmt_8_heap_head = ___c_pmt_8_heap;
    ___c_pmt_8_heap_end = (char *) ___c_pmt_8_heap + HEAP8_SIZE;
    char * pmem_ptr = (char *)___c_pmt_8_heap;
    align_char_to(8, &pmem_ptr);
    ___c_pmt_8_heap = pmem_ptr;
    ___c_pmt_64_heap = malloc(HEAP64_SIZE);
    ___c_pmt_64_heap_head = ___c_pmt_64_heap;
    ___c_pmt_64_heap_end = (char *) ___c_pmt_64_heap + HEAP64_SIZE;
    pmem_ptr = (char *)___c_pmt_64_heap;
    align_char_to(64, &pmem_ptr);
    ___c_pmt_64_heap = pmem_ptr;
    prometeo_tic(&timer1);
	void *callee_pmt_8_heap = ___c_pmt_8_heap;
	void *callee_pmt_64_heap = ___c_pmt_64_heap;

    struct pvec * ___pmt_v0 = c_pmt_create_pvec(n);
    struct pmat * ___pmt_m1 = c_pmt_create_pmat(n, n);
    struct pmat * A = c_pmt_create_pmat(n, n);
    struct pmat * B = c_pmt_create_pmat(n, m);
    struct pmat * Q = c_pmt_create_pmat(n, n);
    struct pmat * R = c_pmt_create_pmat(m, m);
    struct pmat * P = c_pmt_create_pmat(n, n);
    struct pmat * K = c_pmt_create_pmat(m, n);
    struct pvec * x = c_pmt_create_pvec(n);
    double h = 0.1;
    c_pmt_pmat_set_el(A, 0, 0, 1.0);
    c_pmt_pmat_set_el(A, 0, 1, h);
    c_pmt_pmat_set_el(A, 1, 1, 1.0);
    c_pmt_pmat_set_el(B, 1, 0, h);
    c_pmt_pmat_set_el(Q, 0, 0, 1.0);
    c_pmt_pmat_set_el(Q, 1, 1, 0.1);
    c_pmt_pmat_set_el(R, 0, 0, 0.01);
    _Z3lqrpmatpmatpmatpmatpmatpmat(A, B, Q, R, P, K);
    c_pmt_pmat_print(K);
    c_pmt_pvec_set_el(x, 0, 1.0);
    c_pmt_pvec_fill_view(0.0, ___pmt_v0, 0, -1);
    c_pmt_gemv_view_t(1.0, P, 0, 0, -1, -1, x, 0, -1, 1.0, ___pmt_v0, 0, -1, ___pmt_v0, 0, -1);
    double ___pmt_s1 = c_pmt_pvec_dot_view(___pmt_v0, 0, -1, x, 0, -1);
    printf("cost-to-go: %f\n\n", 0.5 * ___pmt_s1);

    for(int t = 0, ___pmt_end_2 = 50; t < ___pmt_end_2; t += 1) {
        c_pmt_pvec_fill_view(0.0, ___pmt_v0, 0, -1);
        c_pmt_pmat_copy(A, ___pmt_m1);
        c_pmt_gemm_ab_nn(1.0, B, K, 1.0, ___pmt_m1, ___pmt_m1);
        c_pmt_gemv_view_n(1.0, ___pmt_m1, 0, 0, -1, -1, x, 0, -1, 1.0, ___pmt_v0, 0, -1, ___pmt_v0, 0, -1);
        c_pmt_pvec_copy_view(___pmt_v0, 0, -1, x, 0, -1);
    }

    printf("state after 5 s: %e\n\n", c_pmt_pvec_get_el(x, 0));

	___c_pmt_8_heap = callee_pmt_8_heap;
	___c_pmt_64_heap = callee_pmt_64_heap;

	execution_time = prometeo_toc(&timer1);
	printf("execution time:%fs\n", execution_time);
	free(___c_pmt_8_heap_head);
	free(___c_pmt_64_heap_head);
	total_time = prometeo_toc(&timer0);
	printf("total time:%fs", total_time);
	return 0;
}
