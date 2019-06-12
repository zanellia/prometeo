CC = gcc
CFLAGS += -g -fPIC

INSTALL_DIR = /opt/prometeo
SRCS += simple_example.c 
CFLAGS+=-I$(INSTALL_DIR)/include -I/opt/blasfeo/include
LIBPATH+=-L$(INSTALL_DIR)/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o simple_example $(CFLAGS)  $(SRCS)  -lcprmt -lblasfeo -lm

clean:
	rm -f *.o

