CC = gcc
CFLAGS += -O2 -fPIC

SRCS += prmt_mat_blasfeo_wrapper.c
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

shared: all
	$(CC) -shared -o libcprmt.so *.o
	# mv libcprmt.so ./lib/
clean:
	rm -f *.o
	rm -f *.so
