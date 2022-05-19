import ast
import astpretty as ap
# import typing
import sys
import argparse
import prometeo
import os
import platform
import subprocess
from strip_hints import strip_file_to_string
import json
import numpy as np

# from prometeo.mem.ast_analyzer import compute_reach_graph
from prometeo.mem.ast_analyzer import ast_visitor
from prometeo.mem.ast_analyzer import compute_reach_graph

from copy import deepcopy

import casadi as ca
import time
import re
from collections import OrderedDict
import numexpr

size_of_pointer = 8
size_of_int = 4
size_of_double = 8

makefile_template = '''
CC = gcc
CFLAGS += -fPIC -std=c99
HEAP64_SIZE = {{ HEAP64_SIZE }}
HEAP8_SIZE = {{ HEAP8_SIZE }}

INSTALL_DIR = {{ INSTALL_DIR }}
SRCS += {{ filename }}.c
CFLAGS+=-I$(INSTALL_DIR)/include/blasfeo -I$(INSTALL_DIR)/include/prometeo
CFLAGS+=-DHEAP64_SIZE=$(HEAP64_SIZE)
CFLAGS+=-DHEAP8_SIZE=$(HEAP8_SIZE)
LIBPATH+=-L$(INSTALL_DIR)/lib/blasfeo -L$(INSTALL_DIR)/lib/prometeo

{{ CASADI_TARGET }}

sources: $(SRCS)
\t$(CC) $(LIBPATH) -o {{ filename }} $(CFLAGS)  $(SRCS) $(OBJS) -lcpmt -lblasfeo -lm

all: casadi sources


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

def resolve_dims_value(dim_vars):
    """
    Resolve value of dims and dimv variables.

    Arguments:

    dim_vars -- ordered dictionary that contains the unresolved dims and dimv variables
    """
    for dim_var1_key, dim_var1_value in dim_vars.items():
        if isinstance(dim_var1_value, list):
            for i in range(len(dim_var1_value)):
                for j in range(len(dim_var1_value[i])):

                    dim_value = dim_var1_value[i][j]
                    # check if the value of dim variables contains chars
                    chars = ''.join(re.split("[^a-zA-Z]*", dim_value)).replace(' ', '')

                    # if there are unresolved dim vars, then chars is non empty
                    if chars:
                        for dim_var2_key, dim_var2_value in dim_vars.items():
                            dim_value = re.sub(r'\b' + dim_var2_key + r'\b', dim_var2_value, dim_var1_value)
                            chars = ''.join(re.split("[^a-zA-Z]*", dim_value)).replace(' ', '')
                            if not chars:
                                break

                    if chars:
                        raise Exception('Could not resolve value {} of dims \
                            variable {}'.format(dim_var1_value, dim_var1_key))

                    dim_var1_value[i][j] = dim_value

        else:
            # check if the value of dim variables contains chars
            chars = ''.join(re.split("[^a-zA-Z]*", dim_var1_value)).replace(' ', '')

            # if there are unresolved dim vars, than chars is non empty
            if chars:
                for dim_var2_key, dim_var2_value in dim_vars.items():
                    if not isinstance(dim_var2_value, list):
                        dim_var1_value = re.sub(r'\b' + dim_var2_key + r'\b', dim_var2_value, dim_var1_value)
                        chars = ''.join(re.split("[^a-zA-Z]*", dim_var1_value)).replace(' ', '')
                        if not chars:
                            break

            if chars:
                raise Exception('Could not resolve value {} of dims variable \
                    {}'.format(dim_var1_value, dim_var1_key))

        dim_vars[dim_var1_key] = dim_var1_value

    return dim_vars

class Graph:
    def __init__(self, nodes, edges, start, end, heap_start):
        """
        Class that describes a graph used to compute 
        the worst-case memory usage of a program.

        Parameters
        ----------
        nodes : list of strings
            list of nodes
        edges : list of [(v1,v2), weight]
            list of edges
        start : str
            name start node
        end : str
            name of end node
        """
        self.nodes = dict()

        for i in range(len(nodes)):
            self.nodes[nodes[i]] = 0

        self.nodes[start] = heap_start
        self.edges = edges
        self.start = start
        self.end = end

    def compute_shortes_path(self, max_iter=10000):
        """
        Compute shortest path (worst-case memory usage) from self.start to self.end
        using Bellman-Ford's algorithm.

        Parameters
        ---------
        max_iter : int
            maximum number of iterations

        Returns
        -------

        path_length : int
            length of shortest path (-worst-case memory usage)
        """
        
        for i in range(len(self.nodes)-1):
            for j in range(len(self.edges)):
                v1 = self.edges[j][0][0]
                v2 = self.edges[j][0][1]
                d_v1 = self.nodes[v1] 
                d_v2 = self.nodes[v2] 
                w = self.edges[j][1]
                if  d_v1 + w < d_v2:
                    self.nodes[self.edges[j][0][1]] = d_v1 + w

        # check for negative cycles
        for j in range(len(self.edges)):
            v1 = self.edges[j][0][0]
            v2 = self.edges[j][0][1]
            d_v1 = self.nodes[v1] 
            d_v2 = self.nodes[v2] 
            w = self.edges[j][1]
            if  d_v1 + w < d_v2:
                raise Exception('Negative cycle detected in call graph!')

        return self.nodes[self.end]

def pmt_main():
    """
    Method called by prometeo's command line utility `pmt`
    """

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
        code_no_hints = strip_file_to_string(filename) + post

        tic = time.time()
        exec(code_no_hints, globals(), globals())
        toc = time.time() - tic
        print('Execution time = {:0.3f} sec'.format(toc))
    else:
        try:
            f = open(filename)
            f.close()
        except FileNotFoundError:
            print('\n\033[;1m > prometeo:\033[0;0m \033[91m file {} not found.\033[0;0m'.format(filename))
            exit()

        print('\n\033[;1m > prometeo:\033[0;0m starting transpilation')
        pmt_path = os.path.dirname(prometeo.__file__)
        filename_ = filename.split('.')[0]
        sed_cmd = "sed '/# pure >/,/# pure </d' " + filename_ + '.py'
        code = ''.join(os.popen(sed_cmd).read())
        tree = ast.parse(code)
        # ap.pprint(tree)
        tree_copy = deepcopy(tree)

        try:
            result  = prometeo.cgen.code_gen_c.to_source(tree, filename_, \
                    main=True,
                    size_of_pointer = size_of_pointer, \
                    size_of_int = size_of_int, \
                    size_of_double = size_of_double)
        except prometeo.cgen.code_gen_c.cgenException as e:
            print('\n > Exception -- prometeo code-gen: ', e.message)
            code = ''.join(open(filename))
            print(' > @ line {}:'.format(e.lineno) + '\033[34m' + \
                code.splitlines()[e.lineno-1] + '\033[0;0m')
            print(' > Exiting.\n')
            if debug:
                raise
            else:
                return 1

        dest_file = open('__pmt_cache__/' + filename_ + '.c', 'w')
        dest_file.write(prometeo.cgen.source_repr.pretty_source(result.source))
        dest_file.close()

        dest_file = open('__pmt_cache__/' + filename_ + '.h', 'w')
        dest_file.write(prometeo.cgen.source_repr.pretty_source(result.header))
        dest_file.close()

        print('\033[;1m > prometeo:\033[0;0m code-generation successfully completed')

        print('\033[;1m > prometeo:\033[0;0m starting worst-case heap usage analysis')
        # compute heap usage

        # load log file
        with open('__pmt_cache__/dim_record.json') as f:
            dim_vars = json.load(f, object_pairs_hook=OrderedDict)

        # reverse ordered dictionary to apply iterative resolution of expressions
        dim_vars = OrderedDict(reversed(list(dim_vars.items())))

        # resolve dims and dimv values
        dim_vars = resolve_dims_value(dim_vars)

        # evaluate numerical expressions
        for key, value in dim_vars.items():
            if isinstance(value, list):
                for i in range(len(value)):
                    for j in range(len(value[i])):
                        dim_vars[key][i][j] = str(numexpr.evaluate(str(value[i][j])))
            else:
                dim_vars[key] = str(numexpr.evaluate(str(value)))

        # load log file
        with open('__pmt_cache__/heap64.json') as f:
            heap64_data = json.load(f)

        # resolve values of heap usage in calls
        for key, value in heap64_data.items():
            for item in dim_vars:
                if item in heap64_data[key]:
                    heap64_data[key] = re.sub(r'\b' + item + r'\b', dim_vars[item], heap64_data[key])

        # evaluate numerical expressions
        for key, value in heap64_data.items():
            heap64_data[key] = str(numexpr.evaluate(str(value)))

        # load log file (8-byte aligned)
        with open('__pmt_cache__/heap8.json') as f:
            heap8_data = json.load(f)

        # resolve values of heap usage in calls
        for key, value in heap8_data.items():
            for item in dim_vars:
                if item in heap8_data[key]:
                    heap8_data[key] = re.sub(r'\b' + item + r'\b', dim_vars[item], heap8_data[key])

        # evaluate numerical expressions
        for key, value in heap8_data.items():
            heap8_data[key] = str(numexpr.evaluate(str(value)))

        visitor = ast_visitor()
        visitor.visit(tree_copy)
        call_graph = visitor.callees
        typed_record = visitor.typed_record
        meta_info = visitor.meta_info
        # print('\ncall graph:\n\n', call_graph, '\n\n')

        reach_map, call_graph = compute_reach_graph(\
            call_graph, typed_record, meta_info)

        # check that there are no cycles containing memory allocations
        for method in reach_map:
            if '*' in reach_map[method] and typed_record[method] != dict():
                raise Exception('\n\nDetected cycle {} containing memory'
                ' allocation.\n'.format(reach_map[method]))

        # update heap usage with memory associated with 
        # constructors (escape memory)

        # load log file
        with open('__pmt_cache__/constructor_record.json') as f:
            constructors_list = json.load(f)

        for caller, callees in call_graph.items():
            for callee in callees:
                # if call is a constructor, then account for 
                # escaped memory
                if callee in constructors_list:
                    heap64_data[caller] = str(int(heap64_data[caller]) 
                        + int(heap64_data[callee]))
                    heap8_data[caller] = str(int(heap8_data[caller]) 
                        + int(heap8_data[callee]))

        # print('reach_map:\n\n', reach_map, '\n\n')

        # Bellman-Ford algorithm
        # build memory graph (64-bytes aligned)
        nodes = []
        edges = []

        for key, value in call_graph.items():
            nodes.append(key)

        for key, value in call_graph.items():

            # if leaf node
            if not value:
                value = ['end']

            for node in value:
                if node in heap64_data:
                    heap_usage = -int(heap64_data[node])
                else:
                    heap_usage = 0

                # import pdb; pdb.set_trace()
                edges.append([(key,node), heap_usage])


        # add artificial end node
        nodes.append('end')

        if 'global@main' in heap64_data:
            heap_main = -int(heap64_data['global@main'])
        else:
            heap_main = 0

        mem_graph = Graph(nodes, edges, 'global@main', 'end', heap_main)
        worst_case_heap_usage_64 = -mem_graph.compute_shortes_path()

        # build memory graph (8-bytes aligned)
        nodes = []
        edges = []

        for key, value in call_graph.items():
            nodes.append(key)

        for key, value in call_graph.items():

            # if leaf node
            if not value:
                value = ['end']

            for node in value:
                if node in heap8_data:
                    heap_usage = -int(heap8_data[node])
                else:
                    heap_usage = 0

                # import pdb; pdb.set_trace()
                edges.append([(key,node), heap_usage])

        # add artificial end node
        nodes.append('end')

        if 'global@main' in heap8_data:
            heap_main = -int(heap8_data['global@main'])
        else:
            heap_main = 0

        mem_graph = Graph(nodes, edges, 'global@main', 'end', heap_main)
        worst_case_heap_usage_8 = -mem_graph.compute_shortes_path()

        print('\033[;1m > prometeo:\033[0;0m heap usage analysis completed successfully\n \
            \033[34m{}\033[0;0m(\033[34m{}\033[0;0m) 64(8)-bytes aligned\n'.format(\
            worst_case_heap_usage_64, worst_case_heap_usage_8))

        # generate Makefile
        makefile_code = makefile_template.replace('{{ filename }}', filename_)

        makefile_code = makefile_code.replace('{{ HEAP8_SIZE }}', str(2*worst_case_heap_usage_8))
        # NOTE: factor 2 due to alignment
        makefile_code = makefile_code.replace('{{ HEAP64_SIZE }}', str(2*worst_case_heap_usage_64))

        makefile_code = makefile_code.replace('\n','', 1)
        makefile_code = makefile_code.replace('{{ INSTALL_DIR }}', os.path.dirname(__file__) + '/..')

        with open('__pmt_cache__/casadi_funs.json') as f:
            casadi_funs = json.load(f, object_pairs_hook=OrderedDict)

        casadi_target_code = '\nOBJS = '
        for item in casadi_funs:
            fun_name = item.replace('@', '_')
            casadi_target_code = casadi_target_code + ' ' + 'casadi_wrapper_' + fun_name + '.o ' + fun_name + '.o'

        casadi_target_code = casadi_target_code + '\n\ncasadi: ' 

        for item in casadi_funs:
            fun_name = item.replace('@', '_')
            casadi_target_code = casadi_target_code + ' ' + fun_name

        for item in casadi_funs:
            fun_name = item.replace('@', '_')
            casadi_target_code = casadi_target_code + '\n\n'
            casadi_target_code = casadi_target_code + fun_name + ':\n' 
            casadi_target_code = casadi_target_code + "\t$(CC) -c " + fun_name + '.c ' + 'casadi_wrapper_' + fun_name + '.c\n'

        makefile_code = makefile_code.replace('{{ CASADI_TARGET }}', casadi_target_code)
        dest_file = open('__pmt_cache__/Makefile', 'w+')
        dest_file.write(makefile_code)
        dest_file.close()

        print('\033[;1m > prometeo:\033[0;0m building C code')

        os.chdir('__pmt_cache__')
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

        proc = subprocess.Popen(["make", "all"], stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate(timeout=20)
        except TimeOutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print('Command \'make \' timed out.')
        if proc.returncode:
            raise Exception('Command \'make\' failed with the above error.'
             ' Full command is:\n\n {}'.format(outs.decode()))

        print('\033[;1m > prometeo:\033[0;0m successfully built C code')

        print('\033[;1m > prometeo:\033[0;0m running compiled C code:\n')

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

        tic = time.time()
        proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)

        try:
            outs, errs = proc.communicate()
        except TimeOutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print('Command {} timed out.'.format(cmd))
            if red_stdout is not None:
                with open(red_stdout, 'w') as f:
                    f.write(outs)
        toc = time.time() - tic

        if red_stdout is not None:
            with open(red_stdout, 'w') as f:
                f.write(outs.decode())
        else:
            print(outs.decode())

        if proc.returncode:
            raise Exception('Command {} failed with the above error.'
             ' Full command is:\n\n {}'.format(cmd, outs.decode()))
        print('\n\033[;1m > prometeo:\033[0;0m exiting\n')

        os.chdir('..')
