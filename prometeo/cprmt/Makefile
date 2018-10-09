CC = gcc
CFLAGS += -O2 -fPIC

SRCS += prmt_mat_blasfeo_wrapper.c
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

clean:
	rm -f *.o
