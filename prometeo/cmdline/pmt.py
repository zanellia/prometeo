import ast
import astpretty
# import typing
import sys
import argparse
import prometeo
import os
from strip_hints import strip_file_to_string

from prometeo.mem.ast_analyzer import compute_reach_graph
from prometeo.mem.ast_analyzer_2 import ast_visitor
from prometeo.mem.ast_analyzer_2 import compute_reach_graph

from copy import deepcopy

size_of_pointer = 8
size_of_int = 4
size_of_double = 8

makefile_template = '''
CC = gcc
CFLAGS += -fPIC -std=c99

INSTALL_DIR = ../../prometeo/cpmt/install
SRCS += {{ filename }}.c 
CFLAGS+=-I$(INSTALL_DIR)/blasfeo/include -I$(INSTALL_DIR)/prometeo/include
LIBPATH+=-L$(INSTALL_DIR)/blasfeo/lib -L$(INSTALL_DIR)/prometeo/lib

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
        # tree will be slightly modified by 
        # to source(). Store a copy, for heap usage 
        # analysis:
        tree_copy = deepcopy(tree)
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

        # compute heap usage
        visitor = ast_visitor()
        # import pdb; pdb.set_trace()
        visitor.visit(tree_copy) 
        call_graph = visitor.callees
        typed_record = visitor.typed_record
        print('\ncall graph:\n\n', call_graph, '\n\n')

        reach_map = compute_reach_graph(call_graph, typed_record)
        print('reach_map:\n\n', reach_map, '\n\n')

        # check that there are no cycles containing memory allocations
        for method in reach_map:
            if '*' in reach_map[method] and typed_record[method] != dict():
                raise Exception('\n\nDetected cycle {} containing memory allocation.\n'.format(reach_map[method]))

        os.system('make clean')
        os.system('make')
        if sys.platform == 'darwin':
            DYLD_LIBRARY_PATH = os.getenv('DYLD_LIBRARY_PATH')
            cmd = './' + filename_
            sys.exit(os.system('export DYLD_LIBRARY_PATH={} && '.format(DYLD_LIBRARY_PATH) + cmd))
        else:
            cmd = './' + filename_
            sys.exit(os.system(cmd))
