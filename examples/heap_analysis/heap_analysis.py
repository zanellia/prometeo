from prometeo import *

n :dims = 10
m :dims = 10

# (ps + m -1)*(nc + n - 1) + (m + n + bs*nc -1)
# ps = 4, nc = 4
# -> 1 pmat = (204 + 64)*8 = 2144

# worst-case path is [main -> f1 -> f2 -> f3] (10 pmats = 21440 bytes)

def f1() -> None:
    A : pmat = pmat(n,n)
    B : pmat = pmat(n,n)
    C : pmat = pmat(n,n)
    f3()
    return

def f2() -> None:
    A : pmat = pmat(n,n)
    B : pmat = pmat(n,n)
    f1()
    f3()
    return

def f3() -> None:
    A : pmat = pmat(n,n)
    B : pmat = pmat(n,n)
    C : pmat = pmat(n,n)
    D : pmat = pmat(n,n)
    E : pmat = pmat(n,n)
    return

def main() -> int:
    f1()
    f2()
    return 0
