from prometeo import *

n : dims = 10

class ClassA():
    A : pmat = pmat(n,n)

    def method1(self, arg1 : int) -> int:
        return 0

class ClassB():
    B : ClassA = ClassA()

def main() -> int:
    A : pmat = pmat(n,n)
    D : ClassA = ClassA()
    return 0
# def main() -> int:
#     A : pmat = pmat(n,n)
#     E : ClassB = ClassB()
#     return 0

