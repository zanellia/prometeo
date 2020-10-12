# from prometeo import * 

def fib(n):
    a : int = 0
    b : int = 1
    for i in range(n):
        a = b
        b =  a + b
    return a

import time
start = time.time()
res : int = 0

for i in range(10000000):
    res = fib(30)

print('%i' %res)
end = time.time()
print('execution time = ', end - start)

# def main() -> int:
 
#     res : int = 0

#     for i in range(10000000):
#         res = fib(30)

#     print('%i' %res)
#     return 0
