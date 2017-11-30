class p_class:
    attr_1: int = 1
    attr_2: double = 3.0

    def method_1(arg1: double, arg2: double) -> double:
        a: double = arg1.field1
        b: double = arg2.field2
        copyarg2: double = arg2
        c: double = a*b + b*a*a

        return c

    def method_2(arg1: double) -> double:
        c: double = arg1*arg1
        return c

    def loop_method(arg1: int) -> int:
        res: int = 0
        for i in range(arg1):
            res = res + 1
        return res
