def function1(arg1, arg2):
    function2(arg1, arg2)
    return

def function2(arg1, arg2):
    function3(arg1, arg2)
    return

def function3(arg1, arg2):
    function1(arg1, arg2)
    return

def function4(arg1, arg2):
    return



