from prometeo import *

def foo(a : int) -> int:
    return a

class Number:
    def __init__(self) -> None:
        self.value: int = 1

    def get_value(self) -> int:

        return self.value

class Simple_class:
    def __init__(self) -> None:
        self.a: int = 1
        self.number : Number = Number()

    # def method1(self) -> int:

    #     return self.a

    def method1(self, b : int) -> int:
        
        c : int = self.a + b

        return c

def main() -> int:

    S : Simple_class = Simple_class()
    a : int = 1
    # b : float = 1.0
    a = foo(a)
    a = S.method1(a)
    a = S.method1(S.number.value)
    a = S.number.get_value()
    a = S.number.value
    a = S.number.get_value()

    return 0
