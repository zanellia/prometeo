CC = gcc
CFLAGS += -g -fPIC

SRCS += dgemm.c 
CFLAGS+=-I/opt/prometeo/include -I/opt/blasfeo/include
LIBPATH+=-L/opt/prometeo/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o dgemm $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o

