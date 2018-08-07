from malloc_wrapper import *
from memory_manager import *

memory_manager.use_prmt_heap = 0
memory_manager.prmt_heap_head = prmt_malloc(64*10)
address = memory_manager.prmt_alloc_p(10)
print(address)
memory_manager.use_prmt_heap = 1
address = memory_manager.prmt_alloc_p(10)
print(address)
address = memory_manager.prmt_alloc_p(10)
print(address)
