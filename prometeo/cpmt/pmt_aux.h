#ifndef PMT_AUX_H_
#define PMT_AUX_H_

#ifdef __cplusplus
extern "C" {
#endif

int align_char_to(int num, char **c_ptr);
void c_pmt_check_heap(void);
int c_pmt_imin(int a, int b);
int c_pmt_imax(int a, int b);

#ifdef __cplusplus
}
#endif

#endif // PMT_AUX_H_
