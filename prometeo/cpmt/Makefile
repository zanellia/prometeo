CC = gcc
# CC = g++
# CC = clang
CFLAGS = -std=c99
CFLAGS += -fPIC
PREFIX = ./install

SRCS += pmat_blasfeo_wrapper.c
SRCS += pvec_blasfeo_wrapper.c
SRCS += pmt_aux.c
CFLAGS+=-I../../external/blasfeo/include/

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

blasfeo:
	( cd ../../external/blasfeo; $(MAKE) static_library -j4 && $(MAKE) shared_library )

shared: all
	$(CC) -shared -o libcpmt.so *.o

install_shared: blasfeo all shared
	mkdir -p $(PREFIX)/blasfeo/lib
	cp -f ../../external/blasfeo/lib/libblasfeo.so $(PREFIX)/blasfeo/lib/
	mkdir -p $(PREFIX)/blasfeo/include
	cp -f ../../external/blasfeo/include/*.h $(PREFIX)/blasfeo/include/
	mkdir -p $(PREFIX)/prometeo/lib
	cp -f ./libcpmt.so $(PREFIX)/prometeo/lib/
	mkdir -p $(PREFIX)/prometeo/include
	cp -f ./*.h $(PREFIX)/prometeo/include/

clean:
	rm -f *.o
	rm -f *.so
