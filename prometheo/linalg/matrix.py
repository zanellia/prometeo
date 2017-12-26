# simple wrapper to scipy.linalg - matrices in row-major format
import scipy as sci
import scipy.linalg as la

class matrix(object):
    m: int                   # number of rows
    n: int                   # number of columns
    data: *PyObject          # data
    mem_type: char           # memory type (volatile/persistent)   
    def __init__(self, m, n, data, mem_type, hard_copy):
        self.m = m
        self.n = n
        self.data = data

def dgemm(alpha, A, B):            
    return  la.blas(alpha, A, B)
