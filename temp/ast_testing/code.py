class p_class:
    p_atrr: int = 1

    def p_method(arg1: float, arg2: float) -> int:
        a: type1 = arg1.field1
        b: type2 = arg2.field2
        copyarg2: type3 = arg2
        c: type4 = a*b + b*a*a

        return c

    def loop_method(arg1: int) -> int:
        res: int = 0
        for i in range(arg1):
            res = res + 1
        return res
