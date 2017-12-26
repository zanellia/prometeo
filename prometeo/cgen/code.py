class p_class:
    attr_1: int = 1
    attr_2: double = 3.0

    def method_1(arg1: type_1, arg2: type_2) -> double:
        a: double = arg1.field1
        b: double = arg2.field2
        copyarg2: double = arg2
        c: double = a*b + b*a*a

        return c

    def method_1(arg1: type_1) -> double:
        a: double = arg1.field1
        b: double = arg1.field2
        copyarg1: double = arg1
        c: double = a*b + b*a*a

        return c
    
    def method_2(arg1: type_1) -> double:
        c: double = arg1*arg1
        return c

    def loop_method(arg1: type_1) -> int:
        res: int = 0
        var1: double = 0
        var1 = self.method_2(arg1)
        
        for i in range(arg1):
            res = res + 1
        return res
