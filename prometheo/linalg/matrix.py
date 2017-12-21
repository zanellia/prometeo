# simple wrapper to scipy.linalg - matrices in row-major format

class matrix(object):
    m = None                 # number of rows
    n = None                 # number of columns
    data = None              # data

    def __init__(self, m, n, data):
        self.m = m
        self.n = n
        self.data = data

def dgemm(alpha, A, B):        
        
