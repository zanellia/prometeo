from ..linalg import pmat
def plist(list_type, sizes):
    if list_type.__name__ == 'pmat':
        ret_list = [list_type]*len(sizes)
        for i in range(len(sizes)):
            ret_list[i] = pmat(sizes[i][0], sizes[i][1])
    elif list_type.__name__ == 'pvec':
        ret_list = [list_type]*len(sizes)
        for i in range(len(sizes)):
            ret_list[i] = pvec(sizes[i][0])
    elif list_type.__name__ == 'int':
        ret_list = [list_type]*sizes
        for i in range(sizes):
            ret_list[i] = 0
    elif list_type.__name__ == 'float':
        ret_list = [list_type]*sizes
        for i in range(sizes):
            ret_list[i] = 0.0
    else:
        raise Exception('Invalid List type: valid types are [pmat, pvec, int, float]. You have {}'.format(list_type))

    return ret_list 
