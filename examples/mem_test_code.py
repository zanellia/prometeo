def method_1():
    method_2()
    method_3()
    return

def method_2():
    method_3()
    method_1()
    return

def method_3():
    return

def method_4():
    method_5()
    return

def method_5():
    method_6()
    method_7()
    return


def method_6():
    method_5()
    method_7()
    return

def method_7():
    # method_6()
    return
