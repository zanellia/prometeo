# Test assignments

from prometeo import *

n : dims = 3

def main() -> int:

    # integer declaration 
    int_var : int = 1
    print('int variable declaration:\n%i\n' %int_var)

    # float declaration 
    float_var : float = 1.0
    print('float variable declaration:\n%f\n' %float_var)

    # pvec declaration
    pvec_var : pvec = pvec(n)
    print('pvec variable declaration:')
    pvec_print(pvec_var)

    # pmat declaration
    pmat_var: pmat = pmat(n, n)
    print('pmat variable declaration:')
    pmat_print(pmat_var)
    # pmat_print(asd)

    # float to pvec
    pvec_var[0] = float_var
    print('float to pvec:')
    pvec_print(pvec_var)

    # float (const) to pvec
    pvec_var[1] = 3.0
    print('float (const) to pvec:')
    pvec_print(pvec_var)

    # float to pmat
    pmat_var[0,1] = float_var
    print('float to pmat:')
    pmat_print(pmat_var)

    # float (const) to pmat 
    pmat_var[1,1] = 2.0
    print('float (const) to pmat:')
    pmat_print(pmat_var)

    # pvec to float
    float_var = pvec_var[0]
    print('pvec to float:\n%f\n' %float_var)

    # pmat to float
    float_var = pmat_var[1, 1]
    print('pmat to float:\n%f\n' %float_var)

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
