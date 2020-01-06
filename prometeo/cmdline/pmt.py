import ast
import astpretty
# import typing
import sys
import argparse
import prometeo
import os
from strip_hints import strip_file_to_string

size_of_pointer = 8
size_of_int = 4
size_of_double = 8

makefile_template = '''
CC = gcc
CFLAGS += -g -fPIC

INSTALL_DIR = /opt/prometeo
SRCS += {{ filename }}.c 
CFLAGS+=-I$(INSTALL_DIR)/include -I/opt/blasfeo/include
LIBPATH+=-L$(INSTALL_DIR)/lib -L/opt/blasfeo/lib 

all: $(SRCS) 
	$(CC) $(LIBPATH) -o {{ filename }} $(CFLAGS)  $(SRCS)  -lcpmt -lblasfeo -lm

clean:
	rm -f *.o {{ filename }}
'''
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('True', 'true', 1):
        return True
    elif v.lower() in ('False', 'false', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def pmt_main(script_path, stdout, stderr, args = None): 

    parser = argparse.ArgumentParser()
    parser.add_argument("program_name", \
            help="name of the prometeo script to be executed")

    parser.add_argument("--cgen", type=str2bool, default="False", \
            help="generate, compile and execute C code?")

    args = parser.parse_args()
    filename = args.program_name
    cgen = args.cgen

    if cgen is False:
        post = '''main()'''
        # code = open(filename).read() + post
        # exec(code, globals(), globals())
        code_no_hints = strip_file_to_string(filename) + post
        exec(code_no_hints, globals(), globals())
    else:
        pmt_path = os.path.dirname(prometeo.__file__)
        # cmd = 'export MYPYPATH=' + pmt_path + ' & mypy ' + filename
        # os.system(cmd)
        filename_ = filename.split('.')[0]
        tree = ast.parse(''.join(open(filename)))
        # astpretty.pprint(tree)
        # import pdb; pdb.set_trace()

        result  = prometeo.cgen.code_gen_c.to_source(tree, filename_, \
                main=True, ___c_pmt_8_heap_size=10000, \
                ___c_pmt_64_heap_size=1000000, \
                size_of_pointer = size_of_pointer, \
                size_of_int = size_of_int, \
                size_of_double = size_of_double)

        dest_file = open(filename_ + '.c', 'w')
        dest_file.write(prometeo.cgen.source_repr.pretty_source(result.source))
        dest_file.close()

        dest_file = open(filename_ + '.h', 'w')
        dest_file.write(prometeo.cgen.source_repr.pretty_source(result.header))
        dest_file.close()

        # generate Makefile
        makefile_code = makefile_template.replace('{{ filename }}', filename_)
        # execname_ = re.sub('\.c$', '', filename_)
        # makefile_code = makefile_template.replace('{{ execname }}', execname_)
        makefile_code = makefile_code.replace('\n','', 1)
        dest_file = open('Makefile', 'w+')
        dest_file.write(makefile_code)
        dest_file.close()

        os.system('make clean')
        os.system('make')
        # import pdb; pdb.set_trace()
        cmd = './' + filename_
        os.system(cmd)
