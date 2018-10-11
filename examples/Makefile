CC = gcc
CFLAGS += -O2 -fPIC

SRCS += dgemm_mod.c 
CFLAGS+=-I../prometeo/cprmt/ -I../external/blasfeo/include/
CFLAGS+=-L../prometeo/cprmt/ 

all: $(SRCS) 
	$(CC) -o dgemm_mod $(CFLAGS) $(SRCS) -lcprmt.so 

clean:
	rm -f *.o

