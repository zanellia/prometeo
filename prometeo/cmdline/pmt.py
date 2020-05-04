import ast
import astpretty
# import typing
import sys
import argparse
import prometeo
import os
import platform
import subprocess
from strip_hints import strip_file_to_string

# from prometeo.mem.ast_analyzer import compute_reach_graph
from prometeo.mem.ast_analyzer import ast_visitor
from prometeo.mem.ast_analyzer import compute_reach_graph

from copy import deepcopy

import casadi as ca

size_of_pointer = 8
size_of_int = 4
size_of_double = 8

makefile_template = '''
CC = gcc
CFLAGS += -fPIC -std=c99

INSTALL_DIR = @INSTALL_DIR@
SRCS += {{ filename }}.c 
CFLAGS+=-I$(INSTALL_DIR)/include/blasfeo -I$(INSTALL_DIR)/include/prometeo
LIBPATH+=-L$(INSTALL_DIR)/lib/blasfeo -L$(INSTALL_DIR)/lib/prometeo

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

    parser.add_argument("--out", type=str, default=None, \
            help="redirect output to file")

    parser.add_argument("--debug", type=str, default=False, \
            help="call raise instead of exit() upon Exception")

    args = parser.parse_args()
    filename = args.program_name
    cgen = args.cgen
    red_stdout = args.out
    debug = args.debug

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

        # result  = prometeo.cgen.code_gen_c.to_source(tree, filename_, \
        #         main=True, ___c_pmt_8_heap_size=10000, \
        #         ___c_pmt_64_heap_size=1000000, \
        #         size_of_pointer = size_of_pointer, \
        #         size_of_int = size_of_int, \
        #         size_of_double = size_of_double)
        try:
            result  = prometeo.cgen.code_gen_c.to_source(tree, filename_, \
                    main=True, ___c_pmt_8_heap_size=10000, \
                    ___c_pmt_64_heap_size=1000000, \
                    size_of_pointer = size_of_pointer, \
                    size_of_int = size_of_int, \
                    size_of_double = size_of_double)
        except prometeo.cgen.code_gen_c.cgenException as e:
            print('\n > Exception -- prometeo code-gen: ', e.message)
            code = ''.join(open(filename))
            print(' > @ line {}:'.format(e.lineno) + '\033[34m' + code.splitlines()[e.lineno-1] + '\033[0;0m')
            print(' > Exiting.\n')
            if debug:
                raise
            else:
                exit()

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
        makefile_code = makefile_code.replace('@INSTALL_DIR@', os.path.dirname(__file__) + '/..')
        dest_file = open('Makefile', 'w+')
        dest_file.write(makefile_code)
        dest_file.close()

        # compute heap usage
        visitor = ast_visitor()
        # import pdb; pdb.set_trace()
        visitor.visit(tree_copy) 
        call_graph = visitor.callees
        typed_record = visitor.typed_record
        # print('\ncall graph:\n\n', call_graph, '\n\n')

        reach_map = compute_reach_graph(call_graph, typed_record)
        # print('reach_map:\n\n', reach_map, '\n\n')

        # check that there are no cycles containing memory allocations
        for method in reach_map:
            if '*' in reach_map[method] and typed_record[method] != dict():
                raise Exception('\n\nDetected cycle {} containing memory'
                ' allocation.\n'.format(reach_map[method]))

        proc = subprocess.Popen(["make", "clean"], stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate(timeout=20)
        except TimeOutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print('Command \'make\' timed out.')
        if proc.returncode:
            raise Exception('Command \'make\' failed with the above error.'
             ' Full command is:\n\n {}'.format(outs.decode()))

        proc = subprocess.Popen(["make"], stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate(timeout=20)
        except TimeOutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print('Command \'make\' timed out.')
        if proc.returncode:
            raise Exception('Command \'make\' failed with the above error.'
             ' Full command is:\n\n {}'.format(outs.decode()))

        INSTALL_DIR = os.path.dirname(__file__) + '/..' 

        running_on = platform.system()
        if running_on == 'Linux':
            cmd = 'export LD_LIBRARY_PATH=' + INSTALL_DIR + '/lib/prometeo:' + \
                INSTALL_DIR + '/lib/blasfeo:$LD_LIBRARY_PATH ; ./' + filename_
        elif running_on == 'Darwin':
            cmd = 'export DYLD_LIBRARY_PATH=' + INSTALL_DIR + '/lib/prometeo:' + \
                INSTALL_DIR + '/lib/blasfeo:$DYLD_LIBRARY_PATH ; ./' + filename_
        else:
            raise Exception('Running on unsupported operating system {}'.format(running_on))

        if red_stdout is not None: 
            proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen([cmd], shell=True)

        try:
            outs, errs = proc.communicate()
        except TimeOutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print('Command \'make\' timed out.')
            if red_stdout is not None:
                with open(red_stdout, 'w') as f:
                    f.write(outs)

        if red_stdout is not None:
            with open(red_stdout, 'w') as f:
                f.write(outs.decode())

        if proc.returncode: 
            raise Exception('Command {} failed with the above error.'
             ' Full command is:\n\n {}'.format(cmd, outs.decode()))
