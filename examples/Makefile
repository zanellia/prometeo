CC = gcc
CFLAGS += -O2 -fPIC

SRCS += dgemm_mod.c 
CFLAGS+=-I../prometeo/cprmt/ -I../external/blasfeo/include/
LIBPATH+=-L/home/andrea/prometeo/prometeo/cprmt/ -L/opt/lib/ 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o dgemm_mod $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o

