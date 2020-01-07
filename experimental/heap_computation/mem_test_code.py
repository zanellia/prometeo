def function_1():
    function_2()
    function_3()
    return

def function_2():
    function_3()
    function_1()
    return

def function_3():
    return

# def function_4():
#     function_5()
#     return

# def function_5():
#     function_6()
#     function_7()
#     return


# def function_6():
#     function_5()
#     function_7()
#     return

# def function_7():
#     return

class class1:
    def __init__(self):
        self.a = 1
    def method_1():
        function_1()

def main():
    class_instance = class1()
    # class1.class2.class3.method_1()
    class1.method_1()
    for i in range(2):
        a = 1
