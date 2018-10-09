CC = gcc
CFLAGS += -O2 -fPIC

SRCS += prmt_mat_blasfeo_wrapper.c
CFLAGS+=-I../../external/blasfeo/include/

shared_library: 
	$(CC) $(CFLAGS) -o obj $(SRCS) 
