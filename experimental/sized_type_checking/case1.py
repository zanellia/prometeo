from prometeo import *

n : dims = 10

class ClassA():
    A : pmat = pmat(n,n)

    def method1(self, arg1 : int) -> int:
        return 0

class ClassB():
    attr1 : ClassA = ClassA()

class ClassC():
    attr2 : ClassB = ClassB()

def main() -> int:
    A : pmat = pmat(n,n)
    D : ClassA = ClassA()
    return 0

