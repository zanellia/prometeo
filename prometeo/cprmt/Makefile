CC = gcc
CFLAGS += -g -fPIC
PREFIX = /opt

SRCS += prmt_mat_blasfeo_wrapper.c
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

shared: all
	$(CC) -shared -o libcprmt.so *.o

install_shared: all shared
	mkdir -p $(PREFIX)/prometeo
	mkdir -p $(PREFIX)/prometeo/lib
	cp -f ./libcprmt.so $(PREFIX)/prometeo/lib/
	mkdir -p $(PREFIX)/prometeo/include
	cp -f ./*.h $(PREFIX)/prometeo/include/

clean:
	rm -f *.o
	rm -f *.so
