def method_1():
    for i in range(10):
        method_2()
    method_3()
    return

def method_2():
    method_3()
    method_1()
    return

def method_3():
    method_4()
    return

def method_4():
    method_5()
    return

def method_5():
    method_5()
    return

def method_6():
    method_1()
    return

