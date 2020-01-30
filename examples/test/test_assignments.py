# Test assignments

from prometeo import *

n : dims = 10

def main() -> int:


    # integer 
    int_var : int = 1
    print('int_var = %i' %int_var)

    # float 
    float_var : float = 1.0
    print('float_var = %f' %float_var)

    pmat_var: pmat = pmat(n, n)
    pvec_var : pvec = pvec(10)

    pvec_var[1] = 3.0
    pvec_print(pvec_var)

    # float to pmat
    pmat_var[0,1] = float_var
    pmat_print(pmat_var)

    # float (const) to pmat 
    pmat_var[0,1] = 1.0
    pmat_print(pmat_var)

    # pmat to float
    float_var = pmat_var[0, 1]
    print('float_var = %f' %float_var)

    # float to pvec
    pvec_var[0] = float_var

    # float (const) to pvec 
    pvec_var[0] = 1.0

    # pvec to float
    float_var = pvec_var[0]

    # subscripted pmat to pmat 
    for i in range(2):
        pmat_var[0,i] = pmat_var[0,i]

    # subscripted pvec to pvec
    pvec_var[0] = pvec_var[1]

    # subscripted pmat to pvec
    pvec_var[1] = pmat_var[0, 2]

    # subscripted pvec to pmat
    pmat_var[0, 2] = pvec_var[1]

    return 0
