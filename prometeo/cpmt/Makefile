CC = gcc
# CC = g++
# CC = clang
CFLAGS = -std=c99
CFLAGS += -fPIC
PREFIX = ./..
SRCS += pmat_blasfeo_wrapper.c
SRCS += pvec_blasfeo_wrapper.c
SRCS += pmt_aux.c
CFLAGS +=-I../../external/blasfeo/include/
OPT_LD_FLAGS = 

all: $(SRCS) 
	$(CC) -c $(CFLAGS) $(SRCS) 

blasfeo:
	( cd ../../external/blasfeo; $(MAKE) static_library -j4 && $(MAKE) shared_library )

shared: all
	$(CC) $(OPT_LD_FLAGS) -shared -o libcpmt.so *.o

install_shared: blasfeo all shared
	mkdir -p $(PREFIX)/lib/blasfeo
	cp -f ../../external/blasfeo/lib/libblasfeo.so $(PREFIX)/lib/blasfeo
	mkdir -p $(PREFIX)/include/blasfeo
	cp -f ../../external/blasfeo/include/*.h $(PREFIX)/include/blasfeo
	mkdir -p $(PREFIX)/lib/prometeo
	cp -f ./libcpmt.so $(PREFIX)/lib/prometeo
	mkdir -p $(PREFIX)/include/prometeo
	cp -f ./*.h $(PREFIX)/include/prometeo

clean:
	rm -f *.o
	rm -f *.so
	
clean_all: clean
	( cd ../../external/blasfeo; $(MAKE) deep_clean )
