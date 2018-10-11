CC = gcc
CFLAGS += -O2 -fPIC

SRCS += dgemm_mod.c 
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

shared: all
	$(CC) -o libcprmt.so *.o
clean:
	rm -f *.o
	rm -f *.so

