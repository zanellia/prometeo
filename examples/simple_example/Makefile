CC = gcc
CFLAGS += -g -fPIC

INSTALL_DIR = /opt/prometeo
SRCS += dgemm.c 
CFLAGS+=-I$(INSTALL_DIR)/include -I/opt/blasfeo/include
LIBPATH+=-L$(INSTALL_DIR)/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o dgemm $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o

