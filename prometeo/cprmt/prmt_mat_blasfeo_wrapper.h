#include "blasfeo_common.h"
#include "blasfeo_i_aux_ext_dep.h"
#include "blasfeo_v_aux_ext_dep.h"
#include "blasfeo_d_aux_ext_dep.h"
#include "blasfeo_d_aux.h"
#include "blasfeo_d_kernel.h"
#include "blasfeo_d_blas.h"

// (dummy) prmt_mat wrapper to blasfeo_dmat
struct prmt_mat {
    blasfeo_dmat * bmat;
}
