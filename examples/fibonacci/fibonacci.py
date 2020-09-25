from prometeo import * 

def Fibonacci(n : int) -> int: 
    if n<=0:
        print("Incorrect input")

    elif n==1:
        return 0

    elif n==2:
        return 1
    else:
        a : int = Fibonacci(n-1)
        b : int = Fibonacci(n-2)
        c : int = a + b
        return c
 

# import time
# start = time.time()
# res : int = 0

# res = Fibonacci(40)

# print('%i' %res)
# end = time.time()
# print('execution time = ', end - start)

def main() -> int:
 
    res : int = 0

    res = Fibonacci(40)

    print('%i' %res)
    return 0
