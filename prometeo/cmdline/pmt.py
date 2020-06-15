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

class Node:
    def __init__(self, name, neighbors, weight):
        """
        Represents a node in the memory graph.

        Parameters
        ----------
        name : str
            name of the node
        neighbors : list
            list of strings containing the name of the neighbors.
        weight : int
            negative or zero integer number representing the memory usage
            associated with the node.
        """
        self.name = name
        self.neighbors = neighbors
        self.weight = weight
        self.tentative_distance = np.inf
        self.visited = False

class Graph:
    def __init__(self, nodes, start, end):
        """
        Class that describes a graph used to compute the worst-case memory
        usage of a program.

        Parameters
        ----------
        nodes : list
            list of instances of class Nodes
        start : str
            name start node
        end : str
            name of end node
        """
        self.nodes = OrderedDict()
        for item in nodes:
            self.nodes[item.name] = item
        self.start = start
        self.end = end

    def compute_shortes_path(self, max_iter=10000):
        """
        Compute shortest path (worst-case memory usage) from self.start to self.end
        using Dijsktra's algorithm.

        Parameters
        ---------
        max_iter : int
            mximum number of iterations

        Returns
        -------

        path_length : int
            length of shortest path (-worst-case memory usage)
        """
        visited_nodes = OrderedDict()
        unvisited_nodes = deepcopy(self.nodes)
        unvisited_nodes[self.start].tentative_distance = 0

        current_node = unvisited_nodes[self.start]

        terminate = False

        for i in range(max_iter):
            # look at all neighbors of current node
            for neighbor_name in current_node.neighbors:
                # print('visiting neighbor ', neighbor_name)
                # TODO(andrea): this should not be necessary... *all* reachable node
                # at this stage should be in the call graph (need to update list of methods...)
                if neighbor_name in self.nodes:
                    if neighbor_name in visited_nodes:
                        neighbor = visited_nodes[neighbor_name]
                    else:
                        neighbor = unvisited_nodes[neighbor_name]

                    new_dist = current_node.tentative_distance \
                        + current_node.weight

                    # print('new dist = ', new_dist)
                    # print('neighbor dist = ', neighbor.tentative_distance)
                    if current_node.tentative_distance + current_node.weight < \
                        neighbor.tentative_distance:
                        # update tentative distance
                        new_dist = current_node.tentative_distance \
                            + current_node.weight

                        # print('updating tentative_distance of node {} to value \
                        # {}'.format(neighbor_name, new_dist))
                        neighbor.tentative_distance = current_node.tentative_distance \
                            + current_node.weight

            if terminate:
                break

            # remove current node from unvisited set
            del unvisited_nodes[current_node.name]
            visited_nodes[current_node.name] = current_node

            # print('current node = ', current_node.name)
            # print('removed node = ', current_node.name)

            # no unvisited nodes left
            if not bool(unvisited_nodes):
                terminate = True
            else:
                found_new_current_node = False
                for i in range(len(unvisited_nodes)):
                    for visited_node_k, visited_node_v in visited_nodes.items():
                        if list(unvisited_nodes.items())[i][1].name in \
                                visited_nodes[visited_node_k].neighbors:
                            found_new_current_node = True
                            # update current node
                            current_node = list(unvisited_nodes.items())[i][1]
                            # print('new current node', current_node.name)
                            break
                    if found_new_current_node:
                        break
                if not found_new_current_node:
                    if current_node.name != 'end':
                        raise Exception('Could not find new current node. Current node is {}'.format(current_node.name))
                    else:
                        terminate = True

        path_length = visited_nodes['end'].tentative_distance

        return path_length

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
        print('\n\033[;1m > prometeo:\033[0;0m starting transpilation')
        pmt_path = os.path.dirname(prometeo.__file__)
        filename_ = filename.split('.')[0]
        tree = ast.parse(''.join(open(filename)))
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
                exit()

        dest_file = open(filename_ + '.c', 'w')
        dest_file.write(prometeo.cgen.source_repr.pretty_source(result.source))
        dest_file.close()

        dest_file = open(filename_ + '.h', 'w')
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
        # print('\ncall graph:\n\n', call_graph, '\n\n')

        reach_map, call_graph = compute_reach_graph(call_graph, typed_record)

        # check that there are no cycles containing memory allocations
        for method in reach_map:
            if '*' in reach_map[method] and typed_record[method] != dict():
                raise Exception('\n\nDetected cycle {} containing memory'
                ' allocation.\n'.format(reach_map[method]))

        # update heap usage with memory associated with constructors (escape memory)

        # load log file
        with open('__pmt_cache__/constructor_record.json') as f:
            constructors_list = json.load(f)

        for caller, callees in call_graph.items():
            for callee in callees:
                # if call is a constructor, then account for escaped memory
                if callee in constructors_list:
                    heap64_data[caller] = str(int(heap64_data[caller]) + int(heap64_data[callee]))
                    heap8_data[caller] = str(int(heap8_data[caller]) + int(heap8_data[callee]))

        # print('reach_map:\n\n', reach_map, '\n\n')

        # build memory graph (64-bytes aligned)
        nodes = []
        for key, value in call_graph.items():
            if key in heap64_data:
                heap_usage = int(heap64_data[key])
            else:
                heap_usage = 0
            # if leaf node
            if not value:
                value = ['end']

            nodes.append(Node(key, value, -heap_usage))

        # add artificial end node
        nodes.append(Node('end', [], 0))

        mem_graph = Graph(nodes, 'global@main', 'end')

        worst_case_heap_usage_64 = -mem_graph.compute_shortes_path()

        # build memory graph (8-bytes aligned)
        nodes = []
        for key, value in call_graph.items():
            if key in heap8_data:
                heap_usage = int(heap8_data[key])
            else:
                heap_usage = 0
            # if leaf node
            if not value:
                value = ['end']

            nodes.append(Node(key, value, -heap_usage))

        # add artificial end node
        nodes.append(Node('end', [], 0))

        mem_graph = Graph(nodes, 'global@main', 'end')

        worst_case_heap_usage_8 = -mem_graph.compute_shortes_path()

        print('\033[;1m > prometeo:\033[0;0m heap usage analysis completed successfully\n \
            \033[34m{}\033[0;0m(\033[34m{}\033[0;0m) 64(8)-bytes aligned\n'.format(\
            worst_case_heap_usage_64, worst_case_heap_usage_8))

        # generate Makefile
        makefile_code = makefile_template.replace('{{ filename }}', filename_)

        makefile_code = makefile_code.replace('{{ HEAP8_SIZE }}', str(worst_case_heap_usage_8))
        # NOTE: factor 2 due to alignment
        makefile_code = makefile_code.replace('{{ HEAP64_SIZE }}', str(worst_case_heap_usage_64))

        makefile_code = makefile_code.replace('\n','', 1)
        makefile_code = makefile_code.replace('{{ INSTALL_DIR }}', os.path.dirname(__file__) + '/..')
        dest_file = open('Makefile', 'w+')
        dest_file.write(makefile_code)
        dest_file.close()

        print('\033[;1m > prometeo:\033[0;0m building C code')
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
