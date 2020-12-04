# from prometeo import * 

def fib(n : int) -> int:
    a : int = 0
    b : int = 1
    c : int = 0
    for i in range(n):
        c = a + b
        a = b
        b = c
    return b

import time
start = time.time()
res : int = 0

for i in range(30):
    for j in range(1000000):
        res = fib(i)

print('%i' %res)
end = time.time()
print('execution time = ', end - start)

# def main() -> int:
 
#     res : int = 0

#     for i in range(30):
#         for j in range(1000000):
#             res = fib(i)
#     print('%i' %res)
#     return 0
