CC = gcc
# CC = clang
CFLAGS += -fPIC -std=c99
PREFIX = /opt

SRCS += pmat_blasfeo_wrapper.c
SRCS += pvec_blasfeo_wrapper.c
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

shared: all
	$(CC) -shared -o libcpmt.so *.o

install_shared: all shared
	mkdir -p $(PREFIX)/prometeo
	mkdir -p $(PREFIX)/prometeo/lib
	cp -f ./libcpmt.so $(PREFIX)/prometeo/lib/
	mkdir -p $(PREFIX)/prometeo/include
	cp -f ./*.h $(PREFIX)/prometeo/include/

clean:
	rm -f *.o
	rm -f *.so
