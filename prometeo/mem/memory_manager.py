import malloc_wrapper as mw

class memory_manager:
    
    use_prmt_heap = []
    prmt_heap_head = []

    @classmethod
    def prmt_alloc_p(cls, n_bytes):
        if cls.use_prmt_heap == 0:
            return mw.prmt_malloc(n_bytes)
        else:
            old_heap_head = cls.prmt_heap_head
            cls.prmt_heap_head.value = cls.prmt_heap_head.value + n_bytes
            return old_heap_head 
            



