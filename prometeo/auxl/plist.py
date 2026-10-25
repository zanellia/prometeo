from ..linalg import pmat, pvec

def plist(list_type, sizes):
    # the element type can be given as a type (pmat) or as a string ('pmat')
    if isinstance(list_type, type):
        list_type = list_type.__name__
    if list_type == 'pmat':
        ret_list = [list_type]*len(sizes)
        for i in range(len(sizes)):
            ret_list[i] = pmat(sizes[i][0], sizes[i][1])
    elif list_type == 'pvec':
        ret_list = [list_type]*len(sizes)
        for i in range(len(sizes)):
            ret_list[i] = pvec(sizes[i][0])
    elif list_type == 'int':
        ret_list = [list_type]*sizes
        for i in range(sizes):
            ret_list[i] = 0
    elif list_type == 'float':
        ret_list = [list_type]*sizes
        for i in range(sizes):
            ret_list[i] = 0.0
    else:
        raise Exception('Invalid List type: valid types are [pmat, pvec, int, float]. You have {}'.format(list_type))

    return ret_list 
