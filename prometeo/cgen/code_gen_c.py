# -*- coding: utf-8 -*-
"""
Adapted from the astor library for Python AST manipulation.

Copyright (c) 2018-2020 Andrea Zanelli

This module converts a Python AST into C source code.
"""

# TODO(andrea): in Python 3.8+ a constant string has type ast.Constant. In order to 
# support the latest versions I might need to add checks for ast.Constant.value in order 
# to determine whether a numerical value 
# or a string is used

# TODO(andrea): add utility to asses AST structure

import ast
import astunparse as astu
import sys

from .op_util import get_op_symbol, get_op_precedence, Precedence
from .node_util import ExplicitNodeVisitor
from .string_repr import pretty_string
from .source_repr import pretty_source
from ..laparser.laparser import LAParser
from collections import namedtuple
# import astpretty as ap
from astpretty import pprint as np
import os
import json
from jinja2 import Template
from collections import OrderedDict

import casadi as ca

pmt_temp_functions = {\
        '_Z4pmatdimsdims': 'c_pmt_create_pmat', \
        '_Z4pvecdims': 'c_pmt_create_pvec', \
        '_Z10pmat_printpmat': 'c_pmt_pmat_print', \
        '_Z8pmt_gemmpmatpmatpmat': 'c_pmt_gemm_nn', \
        '_Z8pmt_gemmpmatpmatpmatpmat': 'c_pmt_gemm_nn', \
        '_Z11pmt_gemm_nnpmatpmatpmatpmat': 'c_pmt_gemm_nn', \
        '_Z11pmt_gemm_nnpmatpmatpmat': 'c_pmt_gemm_nn', \
        '_Z11pmt_gemm_ntpmatpmatpmatpmat': 'c_pmt_gemm_nt', \
        '_Z11pmt_gemm_ntpmatpmatpmat': 'c_pmt_gemm_nt', \
        '_Z11pmt_gemm_tnpmatpmatpmatpmat': 'c_pmt_gemm_tn', \
        '_Z11pmt_gemm_tnpmatpmatpmat': 'c_pmt_gemm_tn', \
        '_Z11pmt_gemm_ttpmatpmatpmatpmat': 'c_pmt_gemm_tt', \
        '_Z11pmt_gemm_ttpmatpmatpmat': 'c_pmt_gemm_tt', \
        '_Z8pmt_geadfloatpmatpmat': 'c_pmt_gead', \
        '_Z9pmt_potrfpmatpmat': 'c_pmt_potrf', \
        '_Z10pmt_potrsmpmatpmat': 'c_pmt_potrsm', \
        '_Z9pmat_tranpmatpmat': 'c_pmt_pmat_tran', \
        '_Z9pmat_copypmatpmat': 'c_pmt_pmat_copy', \
        '_Z9pmat_fillpmatfloat': 'c_pmt_pmat_fill', \
        '_Z9pmat_hcatpmatpmatpmat': 'c_pmt_pmat_hcat', \
        '_Z9pmat_vcatpmatpmatpmat': 'c_pmt_pmat_vcat', \
        '_Z10pvec_printpvec': 'c_pmt_pvec_print', \
        '_Z9pvec_copypvecpvec': 'c_pmt_pvec_copy', \
        '_Z5print' : 'printf'}

        # 'pmt_trmm_rlnn': 'c_pmt_trmm_rlnn', \
        # 'pmt_syrk_ln': 'c_pmt_syrk_ln', \
        # 'pmt_getrf': 'c_pmt_getrf', \
        # 'pmt_getrsm': 'c_pmt_getrsm', \
        # 'pmt_getrsv': 'c_pmt_getrsv', \
        # 'pmt_potrsv': 'c_pmt_potrsv', \
        # 'pvec_fill': 'c_pmt_pvec_fill', \
        # 'print': 'printf'}

pmt_temp_types = {\
        'pmat': 'struct pmat *', \
        'pvec': 'struct pvec *', \
        'None': 'void', \
        'NoneType': 'void', \
        'ptr_int': 'int *', \
        'ptr_pmat': 'struct pmat **', \
        'int': 'int', \
        'float': 'double', \
        'dimv': 'dimv', \
        'dims': 'dims'}

# arg_types = {\
#         'pmat': ['int', 'int'], \
#         'pvec': ['int'], \
#         'pmt_gemm_nn': ['pmat', 'pmat', 'pmat', 'pmat'], \
#         'pmt_gemm_tn': ['pmat', 'pmat', 'pmat', 'pmat'], \
#         'pmt_trmm_rlnn': ['pmat', 'pmat', 'pmat'], \
#         'pmt_syrk_ln': ['pmat', 'pmat', 'pmat', 'pmat'], \
#         'pmt_gead':    ['float', 'pmat', 'pmat'], \
#         'pmt_getrf':   ['pmat', 'pmat', 'List'], \
#         'pmt_getrsm':  ['pmat', 'List', 'pmat'], \
#         'pmt_getrsv':  ['pmat', 'List', 'pvec'], \
#         'pmt_potrf':   ['pmat', 'pmat'], \
#         'pmt_potrsm':  ['pmat', 'pmat'], \
#         'pmt_potrsv':  ['pmat', 'pvec'], \
#         'pmat_fill':   ['pmat', 'float'], \
#         'pmat_copy':   ['pmat', 'pmat'], \
#         'pmat_tran':   ['pmat', 'pmat'], \
#         'pmat_vcat':   ['pmat', 'pmat', 'pmat'], \
#         'pmat_hcat':   ['pmat', 'pmat', 'pmat'], \
#         'pmat_print':  ['pmat'], \
#         'pvec_fill':   ['pvec', 'float'], \
#         'pvec_copy':   ['pvec', 'pvec', 'pmat', 'pmat'], \
#         'pvec_print':  ['pmat', 'pmat', 'pmat', 'pmat'], \
# }

native_types = ['int', 'float']

legacy_classinfo = ["ast.Num", "ast.Str"]

def my_isinstance(obj, classinfo):
    if classinfo in legacy_classinfo:
        if classinfo == "ast.Num":
            if isinstance(obj, ast.Constant):
                if isinstance(obj.value, int) or isinstance(obj.value, float): 
                    return True
                else:
                    return False
            else:
                return False
        if classinfo == "ast.Str":
            if isinstance(obj, ast.Constant):
                if isinstance(obj.value, str): 
                    return True
                else:
                    return False
            else:
                return False
    else:
        return isinstance(obj, classinfo)

def check_node_structure(node, struct):
    if struct == {}:
        return True
    else:
        res = True
        for key in struct.keys():
            if hasattr(node, key):
                res = res and check_node_structure(getattr(node, key), struct[key])
            else: 
                return False
        return res

def get_slice_value(node):
    if sys.version_info >= (3, 9):
        slice_val = node
    else:
        slice_val = node.value
    return slice_val

class PmtArg:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.tran = None
        self.view = None

class PmtCall:
    def __init__(self, name):
        self.name = name
        self.arg_num = 0
        self.args = []
        self.keywords = None

def recurse_attributes(node):
    if my_isinstance(node, ast.Name):
        return node.id
    elif my_isinstance(node, ast.Attribute):
        return recurse_attributes(node.value) + '->' + node.attr 
    else:
        raise cgenException('Invalid attribute or method {}'.format(node))

def parse_pmt_gemm_args(generator, call, node):

    arg0 = call.args[0].name
    arg1 = call.args[1].name
    arg2 = call.args[2].name

    #default keyords arg values
    alpha = 1.0
    beta = 0.0

    # loop over keywords
    for kw in call.keywords:
        if kw.arg == 'alpha':
            alpha = kw.value.n
        if kw.arg == 'beta':
            beta = kw.value.n

    if len(call.args) > 3:
        arg3 = call.args[3].name
    else:
        arg3 = call.args[2].name

    if call.args[0].tran:
        tranA = 't'
    else:
        tranA = 'n'

    if call.args[1].tran:
        tranB = 't'
    else:
        tranB = 'n'

    if call.args[2].tran:
        raise cgenException('Cannot transpose arg 2 of gemm call', node.lineno)

    if len(call.args) > 3:
        if call.args[3].tran:
            raise cgenException('Cannot transpose arg 3 of gemm call', node.lineno)

    blasfeo_call = \
        "blasfeo_dgemm_{4}{5}({0}->bmat->m, {1}->bmat->n, {0}->bmat->n, {6}, {0}->bmat, 0, 0, {1}->bmat, 0, 0, {7}, {2}->bmat, 0, 0, {3}->bmat, 0, 0);\n".format(arg0, arg1, arg2, arg3, tranA, tranB, alpha, beta)

    generator.write(blasfeo_call, dest = 'src')
    return

blas_api_funs = {'pmt_gemm' : parse_pmt_gemm_args}

usr_temp_types = {}

class cgenException(Exception):
    def __init__(self, message, lineno):
        super().__init__(message)
        self.message = message
        self.lineno = lineno

def to_source(node, module_name, indent_with=' ' * 4, add_line_information=False,
              pretty_string=pretty_string, pretty_source=pretty_source,
              main=False, size_of_pointer=8, size_of_int=4, size_of_double=8):

    """This function can convert a node tree back into python sourcecode.
    This is useful for debugging purposes, especially if you're dealing with
    custom asts not generated by python itself.

    It could be that the sourcecode is evaluable when the AST itself is not
    compilable / evaluable.  The reason for this is that the AST contains some
    more data than regular sourcecode does, which is dropped during
    conversion.

    Each level of indentation is replaced with `indent_with`.  Per default this
    parameter is equal to four spaces as suggested by PEP 8, but it might be
    adjusted to match the application's styleguide.

    If `add_line_information` is set to `True` comments for the line numbers
    of the nodes are added to the output.  This can be used to spot wrong line
    number information of statement nodes.

    """
    generator = SourceGenerator(indent_with, size_of_pointer, \
        size_of_int, size_of_double, add_line_information, pretty_string)

    generator.result.source.append('#include "stdlib.h"\n')
    # generator.result.source.append('#include "pmat_blasfeo_wrapper.h"\n')
    # generator.result.source.append('#include "pvec_blasfeo_wrapper.h"\n')
    # generator.result.source.append('#include "pmt_heap.h"\n')
    generator.result.source.append('#include "%s.h"\n' %(module_name))

    generator.result.source.append('void * ___c_pmt_8_heap;\n')
    generator.result.source.append('void * ___c_pmt_64_heap;\n')
    generator.result.source.append('void * ___c_pmt_8_heap_head;\n')
    generator.result.source.append('void * ___c_pmt_64_heap_head;\n')
    generator.result.header.append('#include "prometeo.h"\n')
    generator.result.header.append('#include "timing.h"\n')
    generator.result.header.append('#include "pmt_aux.h"\n')
    generator.result.header.append('#ifdef __cplusplus\nextern "C" {\n#endif\n\n')


    try:
        generator.visit(node)
    except:
        print('\n > Exception -- prometeo code-gen: \033[1;31mparser error at {}:{}\033[0;0m\n'.format(generator.current_line, generator.current_col))
        raise

    generator.result.source.append('\n')
    if set(generator.result.source[0]) == set('\n'):
        generator.result.source[0] = ''


    generator.result.header.append('#ifdef __cplusplus\n}\n#endif\n\n')
    generator.result.header.append('\n')
    if set(generator.result.header[0]) == set('\n'):
        generator.result.header[0] = ''

    # dump meta-data to JSON file
    pmt_cache_dir = '__pmt_cache__'
    if not os.path.exists(pmt_cache_dir):
        os.mkdir(pmt_cache_dir)

    os.chdir(pmt_cache_dir)
    json_file = 'typed_record.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.typed_record), f, indent=4)
    json_file = 'meta_info.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.meta_info), f, indent=3)
    json_file = 'var_dim_record.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.var_dim_record), f, indent=4)
    json_file = 'dim_record.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.dim_record), f, indent=4)
    json_file = 'usr_types.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(usr_temp_types), f, indent=4)
    json_file = 'heap8.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.heap8_record), f, indent=4)
    json_file = 'heap64.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.heap64_record), f, indent=4)
    json_file = 'constructor_record.json'
    with open(json_file, 'w') as f:
        json.dump(OrderedDict(generator.heap64_record), f, indent=4)
    json_file = 'function_record.json'
    with open(json_file, 'w') as f:
        json.dump(generator.function_record, f, indent=4)
    json_file = 'casadi_funs.json'
    with open(json_file, 'w') as f:
        json.dump(generator.casadi_funs, f, indent=4)
    os.chdir('..')


    return generator.result

def precedence_setter(AST=ast.AST, get_op_precedence=get_op_precedence,
                      my_isinstance=my_isinstance, list=list):
    """ This only uses a closure for performance reasons,
        to reduce the number of attribute lookups.  (set_precedence
        is called a lot of times.)
    """

    def set_precedence(value, *nodes):
        """Set the precedence (of the parent) into the children.
        """
        if my_isinstance(value, AST):
            value = get_op_precedence(value)
        for node in nodes:
            if my_isinstance(node, AST):
                node._pp = value
            elif my_isinstance(node, list):
                set_precedence(value, *node)
            else:
                assert node is None, node

    return set_precedence

set_precedence = precedence_setter()

def descope(current_scope, pop):
    if current_scope.endswith(pop):
        return current_scope[:-len(pop)]
    else:
        raise Exception('Attempt to descope {}, which is \
            not the current scope'.format(pop))

def Num_or_Name(node):
    """
    Return node.n if, if node is of type Num, node.id if node is of type Name
    and -node.n if node is of type UnaryOp and node.op is of type USub
    """
    if my_isinstance(node, "ast.Num"):
        return node.n
    elif my_isinstance(node, ast.Name):
        return node.id
    elif my_isinstance(node, ast.UnaryOp):
        if my_isinstance(node.op, ast.USub):
            return -Num_or_Name(node.operand)
        else:
            raise cgenException('node.op is not of type ast.USub.\n', node.lineno)
    else:
        raise cgenException('node is not of type ast.Num nor ast.Name.\n', node.lineno)

def check_expression(node, binops, unops, usr_types, ast_types, record):
    """
    Return True if node is an expression that uses the operations in binops and unops and
    whose operations are of the types contained in the tuples usr_types and ast_types
    """
    if my_isinstance(node, ast_types):
        return True
    elif my_isinstance(node, ast.Name):
        if node.id in record:
            return True
    else:
        if my_isinstance(node, ast.BinOp):
            if my_isinstance(node.op, binops):
                return check_expression(node.left, binops, unops, usr_types, ast_types, record) \
                    and check_expression(node.right, binops, unops, usr_types, ast_types, record)
            else:
                raise cgenException('unsopported BinOp {}\n'.format(astu.unparse(node)), node.lineno)
        elif my_isinstance(node, ast.UnaryOp):
            if my_isinstance(node.op, unops):
                return check_expression(node.operand, binops, unops, usr_types, ast_types, record)
            else:
                raise cgenException('unsopported UnaryOp {}\n'.format(astu.unparse(node)), node.lineno)
        else:
            raise cgenException('could not resolve expression {}\n'.format(astu.unparse(node)), node.lineno)

# def process_annotation(ann_node):
#     if my_isinstance(ann_node, ast.Name):
#         return ann_node.id
#     elif my_isinstance(ann_node, ast.Subscript):
#         return ann_node.value.id + '[' + Num_or_Name(ann_node.slice.value.elts[0]) + \
#             ',' +  Num_or_Name(ann_node.slice.value.elts[0]) + ']'

# def get_pmt_type_value(node, record):
#     """
#     Return prometeo-type of node.value
#     """
#     # simple value
#     if hasattr(node, 'value'):
#         if my_isinstance(node.value, ast.Name):
#             var_name = Num_or_Name(node)
#             if var_name in record:
#                 return record[var_name]

#         # try to infer basic types
#         if my_isinstance(node.value, ast.Num):
#             import pdb; pdb.set_trace()
#             if my_isinstance(node.ast.Num, int):
#                 return 'int'
#             elif my_isinstance(node.ast.Num, float):
#                 return 'float'
#     else:
#         raise cgenException('Could not determine type of node.value', self.lineno)

class Delimit(object):
    """A context manager that can add enclosing
       delimiters around the output of a
       SourceGenerator method.  By default, the
       parentheses are added, but the enclosed code
       may set discard=True to get rid of them.
    """

    discard = False

    def __init__(self, tree, *args):
        """ use write instead of using result.source directly
            for initial data, because it may flush
            preceding data into result.source.
        """
        delimiters = '()'
        node = None
        op = None
        for arg in args:
            if my_isinstance(arg, ast.AST):
                if node is None:
                    node = arg
                else:
                    op = arg
            else:
                delimiters = arg
        tree.write(delimiters[0], dest = 'src')
        result = self.result = tree.result
        result.source = self.result.source = tree.result.source
        self.index = len(result.source)
        self.closing = delimiters[1]
        if node is not None:
            self.p = p = get_op_precedence(op or node)
            self.pp = pp = tree.get__pp(node)
            self.discard = p >= pp

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        result = self.result
        result.source = self.result.source
        start = self.index - 1
        if self.discard:
            result.source[start] = ''
        else:
            result.source.append(self.closing)

class SourceGenerator(ExplicitNodeVisitor):
    """This visitor is able to transform a well formed syntax tree into C
    source code.

    For more details have a look at the docstring of the `node_to_source`
    function.
    """
    using_unicode_literals = False

    def __init__(self, indent_with, size_of_pointer, size_of_int, size_of_double, \
                add_line_information=False,pretty_string=pretty_string,
                blasfeo_ps = 4, blasfeo_nc = 4):

        self.result = namedtuple('result', 'source header')
        self.result.source = []
        self.result.header = []
        self.indent_with = indent_with
        self.add_line_information = add_line_information
        self.indentation = 0 # Current indentation level
        self.new_lines = 0   # Number of lines to insert before next code
        self.colinfo = 0, 0  # index in result.source of string containing
                             # linefeed, and position of last linefeed in
                             # that string

        self.pretty_string = pretty_string
        AST = ast.AST

        visit = self.visit
        newline = self.newline
        result = self.result
        result.source = self.result.source
        result.header = self.result.header
        append_src = result.source.append
        append_hdr = result.header.append

        self.size_of_pointer = size_of_pointer
        self.size_of_int = size_of_int
        self.size_of_double = size_of_double

        self.blasfeo_ps = blasfeo_ps
        self.blasfeo_nc = blasfeo_nc

        self.typed_record = {'global': dict()}
        self.meta_info = {'global': {'methods' : dict(), 'attributes' : dict()}}
        # self.heap8_record = {'global': dict()}
        self.heap8_record = {'global': "0"}
        # self.heap64_record = {'global': dict()}
        self.heap64_record = {'global': "0"}
        self.scope = 'global'
        self.call_scope = 'global'
        self.casadi_funs = []
        self.var_dim_record = {'global': dict()}
        self.dim_record = dict()
        self.constructor_record = []

        self.function_record = {
            'global': {
                '_Z4pmatdimsdims' : { 
                    'arg_types' : ["dims", "dims"],
                    'ret_type': "pmat"
                },
                '_Z4pvecdims' : { 
                    'arg_types' : ["dims"],
                    'ret_type': "pvec"
                },
                '_Z10pmat_printpmat' : { 
                    'arg_types' : ["pmat"],
                    'ret_type': "None"
                },
                '_Z8pmt_gemmpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z8pmt_gemmpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_nnpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_nnpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_ntpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_ntpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_tnpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_tnpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_ttpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z11pmt_gemm_ttpmatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z8pmt_geadfloatpmatpmat' : { 
                    'arg_types' : ["float", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z9pmt_potrfpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z10pmt_potrsmpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z9pmat_tranpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z9pmat_copypmatpmat' : { 
                    'arg_types' : ["pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z9pmat_fillpmatfloat' : { 
                    'arg_types' : ["pmat", "float"],
                    'ret_type': "None"
                },
                '_Z9pmat_hcatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z9pmat_vcatpmatpmatpmat' : { 
                    'arg_types' : ["pmat", "pmat", "pmat"],
                    'ret_type': "None"
                },
                '_Z10pvec_printpvec' : { 
                    'arg_types' : ["pvec"],
                    'ret_type': "None"
                },
                '_Z9pvec_copypvecpvec' : { 
                    'arg_types' : ["pvec", "pvec"],
                    'ret_type': "None"
                }
            }
        }

        self.in_main = False

        self.current_line = 1
        self.current_col = 1

        def write(*params, dest):
            """ self.write is a closure for performance (to reduce the number
                of attribute lookups).
            """
            for item in params:
                if my_isinstance(item, AST):
                    visit(item)
                elif callable(item):
                    item()
                elif item == '\n':
                    newline()
                else:
                    if dest == 'src':
                        if self.new_lines:
                            append_src('\n' * self.new_lines)
                            self.colinfo = len(result.source), 0
                            append_src(self.indent_with * self.indentation)
                            self.new_lines = 0
                        if item:
                            append_src(item)
                    if dest == 'hdr':
                        if self.new_lines:
                            append_hdr('\n' * self.new_lines)
                            self.colinfo = len(result.header), 0
                            append_hdr(self.indent_with * self.indentation)
                            self.new_lines = 0
                        if item:
                            append_hdr(item)


        self.write = write

    def __getattr__(self, name, defaults=dict(keywords=(),
                    _pp=Precedence.highest).get):
        """ Get an attribute of the node.
            like dict.get (returns None if doesn't exist)
        """
        if not name.startswith('get_'):
            raise AttributeError
        geta = getattr
        shortname = name[4:]
        default = defaults(shortname)

        def getter(node):
            return geta(node, shortname, default)

        setattr(self, name, getter)
        return getter

    def delimit(self, *args):
        return Delimit(self, *args)

    def conditional_write(self, *stuff, dest):
        if stuff[-1] is not None:
            self.write(*stuff, dest = dest)
            # Inform the caller that we wrote
            return True

    def newline(self, node=None, extra=0):
        self.new_lines = max(self.new_lines, 1 + extra)
        if node is not None and self.add_line_information:
            self.write('# line: %s' % node.lineno, dest = 'src')
            self.new_lines = 1

    def get_type_of_node(self, node, scope):
        """
        Get type of AST node. 

        Parameters
        ----------
        node 
            node whose type we want to determine

        scope
            current scope

        Returns
        -------
            type_val : str
                type of expression
            arg_types : dict
                type of arguments (if a Call node is being analyzed, None otherwise)

        """
        if my_isinstance(node, ast.Name):
            if node.id in self.typed_record[scope]:
                type_val = self.typed_record[scope][node.id]
            elif  node.id in self.dim_record:
                type_val = 'dims'
            else:
                raise cgenException('Undefined variable {}'.format(node.id), node.lineno)


            return type_val,  None

        elif my_isinstance(node, "ast.Num"):

            type_val = type(node.n).__name__

            return type_val,  None

        elif my_isinstance(node, "ast.Str"):

            type_val = type(node.value).__name__

            return type_val,  None

        elif my_isinstance(node, ast.NameConstant):
            if node.value == None:
                type_val = None
                return type_val,  None
            else:
                raise cgenException('Undefined type {}'.format(node.value), node.lineno)

        elif my_isinstance(node, ast.BinOp):
            type_l, s  = self.get_type_of_node(node.left, scope)
            type_r, s = self.get_type_of_node(node.right, scope)
            if type_l != type_r:
                raise cgenException("Type mismatch in BinOp: left = {}, \
                    right = {}".format(type_l,type_r), node.lineno)
            return type_l, None

        elif my_isinstance(node, ast.UnaryOp):
            type_val, s  = self.get_type_of_node(node.operand, scope)
            return type_val, None

        elif my_isinstance(node, ast.Subscript):
            if my_isinstance(node.value, ast.Name):
                if node.value.id not in self.typed_record[scope]:
                    raise cgenException('Undefined variable {}'.format(node.id), node.lineno)
                elif self.typed_record[scope][node.value.id] == 'pmat' or \
                        self.typed_record[scope][node.value.id] == 'pvec':
                    return 'float', None
                elif 'List' in self.typed_record[scope][node.value.id]:
                    raise Exception("Not implemented")
            elif my_isinstance(node.value, ast.Attribute):
                type_val, s = self.get_type_of_node(node.value, scope)
                # the type of a subscripted List is given by the type of 
                # its elements
                return type_val.split('[')[1].split(',')[0], None
            else:
                raise cgenException("Invalid node type {}".format(node.value), node.lineno)

        elif my_isinstance(node, ast.Attribute):
            # check if first attr is 'self'
            attr_chain = recurse_attributes(node.value)
            attr_list = attr_chain.split('->')

            if attr_list[0] == 'self':

                class_scope = '@'.join(scope.split('@')[:-1])
                type_val = self.get_type_of_node_rec(node.value, class_scope)
            else:
                type_val = self.get_type_of_node_rec(node.value, scope)

            if node.attr not in self.meta_info[type_val]['attr']:
                raise cgenException('Undefined variable or attribute {}'.format(node.attr), node.lineno)
            if self.meta_info[type_val]['attr'][node.attr] in native_types:
                type_val = self.meta_info[type_val]['attr'][node.attr]
            else:
                type_val = 'global@' + self.meta_info[type_val]['attr'][node.attr]
            return type_val, None

        elif my_isinstance(node, ast.Call):
            if my_isinstance(node.func, ast.Name):
                fun_name = node.func.id
                pre_mangl = '_Z' + str(len(fun_name))
                post_mangl = self.build_arg_mangling(node.args, is_call = True)
                fun_name_m = pre_mangl + fun_name + post_mangl
                # TODO(andrea): add check for casadi functions
                if fun_name_m in self.function_record['global']:
                    type_val = self.function_record['global'][fun_name_m]['ret_type']
                    return type_val, self.function_record['global'][fun_name_m]['arg_types']
                elif fun_name not in self.casadi_functions:
                    return 'pmat'   
                else:
                    raise cgenException('Undefined method {}'.format(fun_name_m), node.lineno)
            elif my_isinstance(node.func, ast.Attribute):
                type_val = self.get_type_of_node_rec(node.func.value, scope)

                fun_name = node.func.attr
                pre_mangl = '_Z' + str(len(fun_name))
                post_mangl = self.build_arg_mangling(node.args, is_call = True)
                fun_name_m = pre_mangl + fun_name + post_mangl

                if fun_name_m not in self.meta_info[type_val]['methods']:
                    raise cgenException('Undefined method {}'.format(fun_name_m), node.lineno)
                arg_types = self.meta_info[type_val]['methods'][fun_name_m]['args']
                type_val = self.meta_info[type_val]['methods'][fun_name_m]['return_type']

                return type_val, arg_types
            else:
                raise cgenException('Parse error.', node.lineno)

    def get_type_of_node_rec(self, node, scope):
        if my_isinstance(node, ast.Name):
            if node.id == 'self':
                type_val = scope
                return type_val
            if node.id not in self.typed_record[scope]:
                raise cgenException('Undefined variable or attribute {}'.format(node.id), node.lineno)
            if self.typed_record[scope][node.id] in native_types:
                type_val = self.typed_record[scope][node.id]
            else:
                type_val = 'global@' + self.typed_record[scope][node.id]
            return type_val
        else:
            if my_isinstance(node, ast.Attribute):
                type_val = self.get_type_of_node_rec(node.value, scope)
                if node.attr not in self.meta_info[type_val]['attr']:
                    raise cgenException('Undefined variable or attribute {}'.format(node.attr), node.lineno)
                if self.meta_info[type_val]['attr'][node.attr] in native_types:
                    type_val = self.meta_info[type_val]['attr'][node.attr]
                else:
                    type_val = 'global@' + self.meta_info[type_val]['attr'][node.attr]
                return type_val

    def fun_in_function_record(self, scope):
        tokens = scope.split('@')

        if tokens[0] in self.function_record:
            return self.fun_in_function_record_rec(tokens[1:], self.function_record[tokens[0]])
        else:
            return False

    def fun_in_function_record_rec(self, tokens, scope):
        if 'ret_type' in scope:
            return True
        elif tokens[0] in scope: 
            return self.fun_in_function_record_rec(tokens[1:], scope[tokens[0]])
        else:
            return False

    def get_ret_type_from_function_record(self, scope):
        tokens = scope.split('@')

        if tokens[0] in self.function_record:
            return self.get_ret_type_from_function_record_rec(tokens[1:], self.function_record[tokens[0]])
        else:
            raise cgenException('Could not resolve scope {}'.format(scope), node.lineno)

    def get_ret_type_from_function_record_rec(self, tokens, scope):
        if 'ret_type' in scope:
            return scope["ret_type"]
        elif tokens[0] in scope: 
            return self.get_ret_type_from_function_record_rec(tokens[1:], scope[tokens[0]])
        else:
            raise cgenException('Could not resolve scope {}'.format(scope), node.lineno)

            
    def body(self, statements):
        self.indentation += 1
        self.write(*statements, dest = 'src')
        self.indentation -= 1

    def body_class(self, statements, name):
        self.indentation += 1

        # class attributes (header)
        self.write_class(*statements, name=name)

        self.write('};', dest = 'hdr')
        self.indentation -= 1

        # method prototypes
        self.write_class_method_prototypes(*statements, name=name)

        self.write('\n', dest = 'src')

        # init
        self.write_class_constructor(*statements, name=name)

        # methods
        self.write_class_methods(*statements, name=name)

    def process_list_type(self, node):

        if node.value.func.id != 'plist':
            raise cgenException('Cannot create Lists without using'
                ' plist constructor.', node.lineno)
        else:
            if len(node.value.args) != 2:
                raise cgenException('Type annotations in List \
                    declaration must have the format \
                    List[<type>, <sizes>]', node.lineno)
            # attribute is a List
            ann = node.value.args[0].value
            dims = Num_or_Name(node.value.args[1])
            # ann = node.annotation.slice.value.elts[0].id
            # dims = Num_or_Name(node.annotation.slice.value.elts[1])

            if my_isinstance(dims, str):
                list_type = 'List[' + ann + ', ' + dims + ']'
            else:
                list_type = 'List[' + ann + ', ' + str(dims) + ']'

            return list_type


            if my_isinstance(dims, str):
                # dimension argument is a variable
                self.typed_record[self.scope][node.target.attr] = \
                    'List[' + ann + ', ' + dims + ']'
                    # TODO(andrea): 
                    # use instead 'dict({type: 'List', "attr": {"ann" : ann, "dims" : dims}})
            else:
                # dimension argument is an integer
                self.typed_record[self.scope][node.target.attr] = \
                    'List[' + ann + ', ' + str(dims) + ']'

    def write_instance_attributes(self, params, name):
        """
        Add instance attributes to struct definition in the header.
        """
        for item in params:
            if my_isinstance(item, ast.AnnAssign):
                # skip non-attribute declarations
                if my_isinstance(item.target, ast.Name):
                    break
                if item.target.value.id != 'self':
                    raise cgenException('Unrecognized attribute declaration', self.lineno)

                set_precedence(item, item.target, item.annotation)
                set_precedence(Precedence.Comma, item.value)
                need_parens = my_isinstance(item.target, ast.Name) and not item.simple
                begin = '(' if need_parens else ''
                end = ')' if need_parens else ''
                annotation = item.annotation
                # annotation = ast.parse(item.annotation.s).body[0]
                # if 'value' in annotation.value.__dict__:
                type_py = annotation.id
                if type_py == 'List':
                    list_type = self.process_list_type(item)
                    self.meta_info[self.scope]['attr'][item.target.attr] = list_type
                else:
                    self.meta_info[self.scope]['attr'][item.target.attr] = type_py

                if type_py == 'List':
                    list_type = self.process_list_type(item)
                    self.typed_record[self.scope][item.target.attr] = list_type
                    # check if dims is not a numerical value
                    # TODO(andrea): fix this for numeric values!
                    ann = item.value.args[0].value
                    if ann in pmt_temp_types:
                        ann = pmt_temp_types[ann]
                    dims = Num_or_Name(item.value.args[1])
                    if my_isinstance(dims, str):
                        dim_list = self.dim_record[dims]
                    
                        if my_isinstance(dim_list, list):
                            array_size = len(dim_list)
                        else:
                            array_size = dim_list

                        # array_size = str(Num_or_Name(item.value.args[1]))
                        # self.statement([], ann, ' ', item.target, '[', array_size, '];')
                    self.write('%s' %ann, ' ', '%s' %item.target.attr, \
                        '[%s' %array_size, '];\n', dest = 'hdr')
                else:
                    # not a List
                    ann = type_py

                    # check for user-defined types
                    if ann in usr_temp_types:
                        self.write('struct %s' %ann, ' ',  item.target.attr, '___;\n', dest = 'hdr')
                        self.write('struct %s *' %ann, ' ',  item.target.attr, ';\n', dest = 'hdr')
                        # self.statement(node, node.annotation, ' ', node.target, '= &', node.target, '___;')
                    else:
                        type_c = pmt_temp_types[type_py]
                        self.write('%s' %type_c, ' ', '%s' %item.target.attr, ';\n', dest = 'hdr')

                        # self.conditional_write(' = ', item.value, ';')
                        self.typed_record[self.scope][item.target.attr] = type_py
                # else:
                #     type_py = annotation.id
                #     type_c = pmt_temp_types[type_py]
                #     self.write('%s' %type_c, ' ', '%s' %item.target.id, ';\n', dest = 'hdr')
                #     # self.conditional_write(' = ', item.value, ';')
                #     self.typed_record[self.scope][item.target.id] = type_py

    def write_class(self, *params, name):
        self.meta_info[self.scope]['attr'] = dict()
        self.meta_info[self.scope]['methods'] = dict()
        for item in params:
            if not my_isinstance(item, ast.FunctionDef):
                raise cgenException('Classes can only contain attributes and methods', item.lineno)
            if item.returns is None:
                raise cgenException('Missing return annotation on class method {}'.format(item.name), item.lineno)

            # additional treatment of  __init__ (declare attributes)
            if item.name == '__init__':
                self.write_instance_attributes(item.body, name=name)
                self.update_constructor_heap(item.body, name=name)

            # build argument mangling
            fun_name = item.name
            f_name_len = len(fun_name)
            pre_mangl = '_Z%s' %f_name_len 
            if len(item.args.args) < 1:
                raise cgenException('First argument in method {} \
                    must be \'self\'. You have \'{}\''.format(item.name, \
                    item.args.args), item.lineno)
            if item.args.args[0].arg != 'self':
                raise cgenException('First argument in method {} \
                    must be \'self\'. You have \'{}\''.format(item.name, \
                    item.args.args[0].arg), item.lineno)
            else: 
                # store self argument
                self_arg = item.args.args[0]
                # pop self from argument list
                item.args.args.pop(0)

            post_mangl = self.build_arg_mangling(item.args)
            fun_name_m = pre_mangl + fun_name + post_mangl
            
            self.meta_info[self.scope]['methods'][fun_name_m] = dict()
            if hasattr(self.get_returns(item), 'id'):
                ret_type = self.get_returns(item).id
            else:
                ret_type = self.get_returns(item).value

            self.meta_info[self.scope]['methods'][fun_name_m]['return_type'] = ret_type

            if ret_type is None: 
                ret_type = 'None'

            if  ret_type in pmt_temp_types:
                ret_type = pmt_temp_types[ret_type]
            else:

                raise cgenException ('Usage of non existing type \
                    \033[91m{}\033[0m'.format(ann), item.lineno)
                # raise cgenException ('Usage of non existing type {}'.format(ret_type))

            if len(item.args.args) > 0:  
                self.write('%s (*%s' % (ret_type, fun_name_m), \
                    ')', '(%s *self, ' %name, \
                    dest = 'hdr')
            else:
                self.write('%s (*%s' % (ret_type, fun_name_m), \
                        ')', '(%s *self' %name, \
                        dest = 'hdr')


            args_list = self.visit_arguments(item.args, 'hdr')
            self.meta_info[self.scope]['methods'][fun_name_m]['args'] = args_list
            # TODO(andrea): implicit call to visit() in write() - make explicit
            self.write(');\n', dest = 'hdr')
            # insert back self argument 
            item.args.args.insert(0, self_arg)
      
    def write_class_method_prototypes(self, *params, name):
        """ self.write is a closure for performance (to reduce the number
            of attribute lookups).
        """
        self.write('\n\n', dest = 'hdr')
        for item in params:
            if my_isinstance(item, ast.FunctionDef):
                # build argument mangling
                f_name_len = len(item.name)
                pre_mangl = '_Z%s' %f_name_len
                if item.args.args[0].arg != 'self':
                    raise cgenException('First argument in method {} \
                        must be \'self\'. You have \'{}\''.format(item.name, \
                        item.args.args[0].arg), item.lineno)
                else:
                    # store self argument
                    self_arg = item.args.args[0]
                    # pop self from argument list
                    item.args.args.pop(0)

                post_mangl = self.build_arg_mangling(item.args)
                if hasattr(self.get_returns(item), 'id'):
                    ret_type = self.get_returns(item).id
                else:
                    ret_type = self.get_returns(item).value

                if ret_type is None:
                    ret_type = 'None'

                if  ret_type in pmt_temp_types:
                    ret_type = pmt_temp_types[ret_type]
                else:
                    raise cgenException ('Usage of non existing type {}'.format(ret_type), \
                        item.lineno)

                if len(item.args.args) > 0:
                    self.write('%s (%s%s%s%s' % (ret_type, pre_mangl, item.name, \
                        post_mangl, name) , '_impl)', '(%s *self, ' %name, dest = 'hdr')
                else:
                    self.write('%s (%s%s%s%s' % (ret_type, pre_mangl, item.name, \
                        post_mangl, name) , '_impl)', '(%s *self' %name, dest = 'hdr')
                arg_list = self.visit_arguments(item.args, 'hdr')

                # update function record
                self.function_record[self.scope] = dict()
                self.function_record[self.scope][item.name] = {"arg_types": arg_list,  "ret_type": ret_type}
                self.write(');\n', dest = 'hdr')
                # insert back self argument
                item.args.args.insert(0, self_arg)


    def update_constructor_heap(self, params, name):
        for item in params:
            if my_isinstance(item, ast.AnnAssign):
                if my_isinstance(item.target, ast.Attribute):
                    if item.target.value.id == 'self':
                        # set_precedence(item, item.target, item.annotation)
                        set_precedence(Precedence.Comma, item.value)
                        need_parens = my_isinstance(item.target, ast.Name) and not item.simple
                        begin = '(' if need_parens else ''
                        end = ')' if need_parens else ''
                        # TODO(andrea): need to fix the code below!
                        ann = item.annotation.id
                        if ann == 'List':

                            if item.value.func.id != 'plist':
                                raise cgenException('Invalid subscripted annotation.',
                                        ' Lists must be created using plist constructor and',
                                        ' the argument of List[] must be a valid type.\n', \
                                        item.lineno)
                            else:
                                # attribute is a List
                                ann = item.value.args[0].value
                                dims = Num_or_Name(item.value.args[1])
                                # ann = item.annotation.slice.value.elts[0].id
                                # dims = Num_or_Name(item.annotation.slice.value.elts[1])
                                if my_isinstance(dims, str):
                                    dim_list = self.dim_record[dims]
                                else:
                                    dim_list = dims
                                if ann == 'pmat':
                                    # build init for List of pmats
                                    for i in range(len(dim_list)):
                                        dim1 = dim_list[i][0] 
                                        dim2 = dim_list[i][1] 

                                        # increment scoped heap usage (3 pointers and 6 ints for pmats)
                                        self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                            '+' + '3*' + str(self.size_of_pointer).replace('\n','')
                                        self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                            '+' + '6*' + str(self.size_of_int).replace('\n','')

                                        # upper bound of blasfeo_dmat memsize
                                        # memsize \leq (ps + m -1)*(nc + n - 1) + (m + n + bs*nc -1)
                                        mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)*' \
                                            '(' + str(self.blasfeo_nc) + '+' + dim2 + ' - 1)+(' + dim1 + '+' + dim2 + '+' + \
                                            str(self.blasfeo_ps) + '*' + str(self.blasfeo_nc) + ' - 1)'

                                        self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                                            '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

                                elif ann == 'pvec':
                                    # build init for List of pvecs
                                    for i in range(len(dim_list)):
                                        self.statement([], 'object->', \
                                            item.target.attr, \
                                            '[', str(i),'] = c_pmt_create_pvec(', \
                                            str(dim_list[i][0]), ');')

                                        # increment scoped heap usage (2 pointers and 3 ints for pvecs)
                                        self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                            '+' + '2*' + str(self.size_of_pointer).replace('\n','')
                                        self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                            '+' + '3*' + str(self.size_of_int).replace('\n','')

                                        # upper bound of blasfeo_dvec memsize
                                        # memsize \leq ps + m -1
                                        mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)'

                                        self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                                            '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

                                # else: do nothing (no init required for "memoryless" objects)
                        # pmat[<n>,<m>] or pvec[<n>]
                        elif ann in ['pmat', 'pvec']:
                            if ann == 'pmat':
                                if item.value.func.id != 'pmat':
                                    raise cgenException('pmat objects need to be declared calling',
                                        'the pmat(<n>, <m>) constructor\n.', item.lineno)

                                if not check_expression(item.value.args[0], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                                    tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                                    raise cgenException('Invalid dimension expression in \
                                        pmat constructor ({})'.format(item.value.args[0]), self.lineno)

                                if not check_expression(item.value.args[1], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                                    tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                                    raise cgenException('Invalid dimension expression in \
                                        pmat constructor ({})'.format(item.value.args[1]), self.lineno)

                                dim1 = astu.unparse(item.value.args[0]).replace('\n','')
                                dim2 = astu.unparse(item.value.args[1]).replace('\n','')

                                #TODO(andrea): need to wrap dim names into tokens to avoid name clashes!!!
                                self.var_dim_record[self.scope][item.target.attr] = [dim1, dim2]

                                # increment scoped heap usage (3 pointers and 6 ints for pmats)
                                self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                    '+' + '3*' + str(self.size_of_pointer).replace('\n','')
                                self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                    '+' + '6*' + str(self.size_of_int).replace('\n','')

                                # upper bound of blasfeo_dmat memsize
                                # memsize \leq (ps + m -1)*(nc + n - 1) + (m + n + bs*nc -1)
                                mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)* ' \
                                    '(' + str(self.blasfeo_nc) + '+' + dim2 + ' - 1)+(' + dim1 + '+' + dim2 + '+' + \
                                    str(self.blasfeo_ps) + '*' + str(self.blasfeo_nc) + ' - 1)'

                                self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                                    '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

                            else:
                                # pvec
                                if item.value.func.id != 'pvec':
                                    raise cgenException('pvec objects need to be declared calling',
                                        'the pvec(<n>, <m>) constructor\n.', item.lineno)
                                dim1 = Num_or_Name(item.value.args[0])
                                ann = item.annotation.value.id
                                self.var_dim_record[self.scope][item.target.attr] = [dim1]

                                # increment scoped heap usage (2 pointers and 3 ints for pvecs)
                                self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                    '+' + '2*' + str(self.size_of_pointer).replace('\n','')
                                self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                                    '+' + '3*' + str(self.size_of_int).replace('\n','')

                                # upper bound of blasfeo_dvec memsize
                                # memsize \leq ps + m -1
                                mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)'

                                self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                                    '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

                            # # add variable to typed record
                            # self.typed_record[self.scope][item.target.attr] = ann
                            # # print('typed_record = \n', self.typed_record, '\n\n')
                            # # print('var_dim_record = \n', self.var_dim_record, '\n\n')
                            # if  ann in pmt_temp_types:
                            #     c_ann = pmt_temp_types[ann]
                            #     # self.statement(item, c_ann, ' ', item.target.attr)
                            # else:
                            #     raise cgenException ('Usage of non existing type {}'.format(ann), \
                            #         item.lineno)
                            # if item.value != None:
                            #     if hasattr(item.value, 'value') is False:
                            #         self.conditional_write('\n', 'object->', \
                            #             item.target, ' = ', item.value, ';', dest = 'src')
                            #     else:
                            #         if item.value.value != None:
                            #             self.conditional_write('\n', 'object->', \
                            #                 item.target, ' = ', item.value, ';', dest = 'src')
                            # else:
                            #     raise cgenException('Cannot declare attribute without'
                            #         ' initialization.\n', item.lineno)
                        # elif ann in usr_temp_types:
                            # self.write('\nobject->', item.target.attr, ' = &(object->', item.target.attr, '___);\n', dest = 'src')
                            # self.write(ann, '_constructor(object->', item.target.attr, ');\n', dest='src')
                        # else:
                            # if item.value != None:
                            #     if hasattr(item.value, 'value') is False:
                            #         self.conditional_write('\n', 'object->', \
                            #             item.target, ' = ', item.value, ';', dest = 'src')
                            #     else:
                            #         if item.value.value != None:
                            #             self.conditional_write('\n', 'object->', \
                            #                 item.target, ' = ', item.value, ';', dest = 'src')
                            # else:
                            #     raise cgenException('Cannot declare attribute without \
                            #         initialization.\n', item.lineno)




    def write_class_constructor(self, *params, name):
        self.write('void ', name, '_constructor(struct ', name, ' *object){', dest = 'src')
        self.indentation += 1
        for item in params:
            if my_isinstance(item, ast.FunctionDef):
                # build argument mangling
                f_name_len = len(item.name)
                pre_mangl = '_Z%s' %f_name_len
                if item.args.args[0].arg != 'self':
                    raise cgenException('First argument in method {} \
                        must be \'self\'. You have \'{}\'.'.format(item.name, \
                        item.args.args[0].arg), item.lineno)
                else:
                    # store self argument
                    self_arg = item.args.args[0]
                    # pop self from argument list
                    item.args.args.pop(0)

                # build argument mangling
                post_mangl = self.build_arg_mangling(item.args)

                self.statement(item, 'object->%s%s%s' %(pre_mangl, \
                    item.name, post_mangl), ' = &', '%s%s%s%s' %(pre_mangl, \
                    item.name, post_mangl, name), '_impl;')

                # insert back self argument
                item.args.args.insert(0, self_arg)

            else:
                cgenException('Cannot declare non-method member or class {}'.format(name), self.lineno)

        # call __init__ transpiled code inside constructor
        self.write('\n\tobject->_Z8__init__(object);\n', dest = 'src')
        self.write('\n}\n', dest = 'src')
        self.indentation -=1

    def write_class_methods(self, *params, name):
        """ self.write is a closure for performance (to reduce the number
            of attribute lookups).
        """
        for item in params:
            if my_isinstance(item, ast.FunctionDef):
                self.decorators(item, 1 if self.indentation else 2)
                # self.write()

                # build argument mangling
                f_name_len = len(item.name)
                pre_mangl = '_Z%s' %f_name_len
                if item.args.args[0].arg != 'self':
                    raise cgenException('First argument in method {} \
                        must be \'self\'. You have \'{}\'.'.format(item.name, \
                        item.args.args[0].arg), item.lineno)
                else:
                    # store self argument
                    self_arg = item.args.args[0]
                    # pop self from argument list
                    item.args.args.pop(0)

                post_mangl = self.build_arg_mangling(item.args)

                if hasattr(self.get_returns(item), 'id'):
                    ret_type = self.get_returns(item).id
                else:
                    ret_type = self.get_returns(item).value

                if ret_type is None:
                    ret_type = 'None'

                if  ret_type in pmt_temp_types:
                    ret_type = pmt_temp_types[ret_type]
                else:
                    raise cgenException ('Usage of non existing type {}.'.format(ret_type), item.lineno)

                if len(item.args.args) > 0:
                    self.statement(item, ret_type, ' %s%s%s%s' % (pre_mangl, \
                            item.name, post_mangl, name), '_impl(', name, ' *self, ')
                else:
                    self.statement(item, ret_type, ' %s%s%s%s' % (pre_mangl, \
                            item.name, post_mangl, name), '_impl(', name, ' *self')

                fun_name_m = pre_mangl + item.name + post_mangl
                self.scope = self.scope + '@' + fun_name_m 
                self.typed_record[self.scope] = dict()
                self.var_dim_record[self.scope] = dict()
                self.heap8_record[self.scope] = '0'
                self.heap64_record[self.scope] = '0'
                self.visit_arguments(item.args, 'src')
                self.write(') {\n', dest = 'src')
                # store current pmt_heap value (and restore before returning)
                self.write('\tvoid *callee_pmt_8_heap = ___c_pmt_8_heap;\n', dest = 'src')
                self.write('\tvoid *callee_pmt_64_heap = ___c_pmt_64_heap;\n', dest = 'src')
                self.body(item.body)
                self.newline(1)
                self.write('}', dest = 'src')
                self.scope = descope(self.scope, '@' + fun_name_m)

                if not self.indentation:
                    self.newline(extra=2)
                # insert back self argument
                item.args.args.insert(0, self_arg)

    def else_body(self, elsewhat):
        if elsewhat:
            self.write('\n', '} else {', dest='src')
            self.body(elsewhat)
        # self.write('\n}', dest = 'src')

    def body_or_else(self, node):
        self.body(node.body)
        self.else_body(node.orelse)

    def visit_arguments(self, node, dest_in):
        # args_list returned for meta-info update
        args_list = []
        want_comma = []

        def write_comma():
            if want_comma:
                self.write(', ', dest = dest_in)
            else:
                want_comma.append(True)

        def loop_args(args, defaults):
            set_precedence(Precedence.Comma, defaults)
            padding = [None] * (len(args) - len(defaults))
            arg_list = []
            for arg, default in zip(args, padding + defaults):
                # fish C type from typed record
                if hasattr(arg.annotation, 'value'):
                    if arg.annotation.value.id == 'pmat':
                        dim1 = Num_or_Name(arg.annotation.slice.value.elts[0])
                        dim2 = Num_or_Name(arg.annotation.slice.value.elts[1])
                        arg_type_py = arg.annotation.value.id
                        self.var_dim_record[self.scope][arg.arg] = [dim1, dim2]
                    elif arg.annotation.value.id == 'pvec':
                        dim1 = Num_or_Name(arg.annotation.slice.value.elts[0])
                        arg_type_py = arg.annotation.value.id
                        self.var_dim_record[self.scope][arg.arg] = [dim1]
                    else:
                        raise cgenException('Subscripted type annotation can \
                            be used only with pmat arguments.\n', arg.lineno)
                elif my_isinstance(arg.annotation, ast.Name):
                    arg_type_py = arg.annotation.id
                else:
                    raise cgenException('Invalid function argument without type annotation', arg.lineno)

                args_list.append(arg_type_py)
                arg_type_c = pmt_temp_types[arg_type_py]
                self.write(write_comma, arg_type_c,' ',arg.arg, dest = dest_in)

                # add variable to typed record
                self.typed_record[self.scope][arg.arg] = arg_type_py
                self.conditional_write('=', default, dest = 'src')

        loop_args(node.args, node.defaults)
        self.conditional_write(write_comma, '*', node.vararg, dest = 'src')

        kwonlyargs = self.get_kwonlyargs(node)
        if kwonlyargs:
            if node.vararg is None:
                self.write(write_comma, '*')
            loop_args(kwonlyargs, node.kw_defaults)
        self.conditional_write(write_comma, '**', node.kwarg, dest = 'src')

        return args_list

    def build_arg_mangling(self, args, is_call = False):
        want_comma = []

        def loop_args_mangl_def(args, defaults):
            """
            Compute post mangling for FunctionDef node

            Parameters:
            ---------

            args: 

            AST node containing the arguments used in the function definition


            defaults:

            AST node containing the arguments defaults

            Returns:
            --------

            post_mangl : str

            String containing the post mangling
            """
            set_precedence(Precedence.Comma, defaults)
            padding = [None] * (len(args) - len(defaults))
            post_mangl = ''

            for arg, default in zip(args, padding + defaults):
                # fish C type from typed record
                if my_isinstance(arg.annotation, ast.Name):
                    arg_type_py = arg.annotation.id
                    post_mangl = post_mangl + arg_type_py
                elif arg.arg != 'self':
                    raise cgenException('Invalid function argument without type annotation', arg.lineno)

            return post_mangl

        def loop_args_mangl(args):
            """
            Compute post mangling for Call node

            Parameters:
            ---------

            args: 

            AST node containing the arguments used in the function call


            defaults:

            AST node containing the arguments defaults

            Returns:
            --------

            post_mangl : str

            String containing the post mangling
            """
            post_mangl = ''
            for arg in args:
                if my_isinstance(arg, "ast.Num"):
                    if my_isinstance(arg.n, int):
                        arg_value = 'int'
                    elif my_isinstance(arg.n, float):
                        arg_value = 'float'
                    else:
                        raise cgenException('Invalid numeric argument.\n', arg.lineno)
                    post_mangl = post_mangl + arg_value
                else:
                    # arg_value = arg.id
                    type_val, s = self.get_type_of_node(arg, self.scope)
                    post_mangl = post_mangl + type_val
            return post_mangl
        # def loop_args_mangl_def(args, defaults):
        #     set_precedence(Precedence.Comma, defaults)
        #     padding = [None] * (len(args) - len(defaults))
        #     arg_mangl = ''
        #     for arg, default in zip(args, padding + defaults):
        #         annotation = arg.annotation
        #         # annotation = ast.parse(arg.annotation.s).body[0]
        #         # if 'value' in annotation.value.__dict__:
        #         if 'value' in annotation.__dict__:
        #             # arg_mangl = arg_mangl + annotation.value.value.id
        #             arg_mangl = arg_mangl + annotation.value.id
        #         else:
        #             # arg_mangl = arg_mangl + annotation.value.id
        #             arg_mangl = arg_mangl + annotation.id
        #     return arg_mangl

        if is_call:
            post_mangl = loop_args_mangl(args)
        else:
            post_mangl = loop_args_mangl_def(args.args, args.defaults)

        return post_mangl

    # def build_arg_mangling_mod(self, args):
    #     want_comma = []

    #     def loop_args_mangl(args):
    #         arg_mangl = ''
    #         for arg in args:
    #             if my_isinstance(arg, ast.Num):
    #                 if my_isinstance(arg.n, int):
    #                     arg_value = 'int'
    #                 elif my_isinstance(arg.n, float):
    #                     arg_value = 'double'
    #                 else:
    #                     raise cgenException('Invalid numeric argument.\n', arg.lineno)
    #                 arg_mangl = arg_mangl + arg_value
    #             else:
    #                 # arg_value = arg.id
    #                 type_val, s = self.get_type_of_node(arg, self.scope)
    #                 arg_mangl = arg_mangl + type_val
    #         return arg_mangl

    #     arg_mangl = loop_args_mangl(args)
    #     return arg_mangl

    def statement(self, node, *params, **kw):
        self.newline(node)
        self.write(*params, dest = 'src')

    def decorators(self, node, extra):
        self.newline(extra=extra)
        for decorator in node.decorator_list:
            self.statement(decorator, '@', decorator)

    def comma_list(self, items, trailing=False):
        set_precedence(Precedence.Comma, *items)
        for idx, item in enumerate(items):
            self.write(', ' if idx else '', item, dest = 'src')
        self.write(',' if trailing else '', dest = 'src')

    # Statements
    def visit_Assign(self, node):

        self.current_line = node.lineno
        self.current_col = node.col_offset
        if 'targets' in node.__dict__:
            if len(node.targets) != 1:
                raise cgenException('Cannot have assignments with a number of \
                    targets other than 1.\n', node.lineno)
            # get type of value
            type_val, arg_types = self.get_type_of_node(node.value, self.scope)
            # get type of target
            type_val_t, arg_types = self.get_type_of_node(node.targets[0], self.scope)
            if type_val != type_val_t:
                raise cgenException('Mismatching types in assignment {} = {}'.format(type_val_t, type_val), node.lineno)
            # check for attributes
            if hasattr(node.targets[0], 'value'):
                if hasattr(node.targets[0].value, 'attr'):
                    if node.targets[0].value.attr not in self.typed_record[self.scope]:
                        raise cgenException('Unknown variable {}.'.format( \
                            node.targets[0].value.attr), node.lineno)
                    # TODO(andrea): need to handle attributes recursively
                    target = node.targets[0].value.attr
                    obj_name = node.targets[0].value.value.id
                    # TODO(andrea): need to compute local scope (find strings
                    # that contain scope and have a string in common with self.scope)
                    # this assumes that the class has been defined in the global scope
                    scope = 'global@' + self.typed_record[self.scope][obj_name]
                else:
                    if node.targets[0].value.id not in self.typed_record[self.scope]:
                        raise cgenException('Unknown variable {}.'.format( \
                                node.targets[0].value.id), node.lineno)
                    target = node.targets[0].value.id
                    scope = self.scope
            else:
                if node.targets[0].id not in self.typed_record[self.scope]:
                    raise cgenException('Unknown variable {}.'.format(node.targets[0].id), node.lineno)
            if type(node.targets[0]) == ast.Subscript:
                if target in self.typed_record[scope]:
                    # map subscript for pmats to blasfeo el assign
                    if self.typed_record[scope][target] == 'pmat':


                        # check for ExtSlices
                        isExtSlice = False
                        if sys.version_info >= (3, 9): 
                            if isinstance(node.targets[0].slice.elts[0], ast.Slice):
                                isExtSlice = True
                        else:
                            if my_isinstance(node.targets[0].slice, ast.ExtSlice):
                                isExtSlice = True

                        if isExtSlice:
                            if sys.version_info >= (3, 9):
                                first_arg = node.targets[0].slice.elts[0]
                                second_arg = node.targets[0].slice.elts[1]
                            else:
                                first_arg = node.targets[0].slice.dims[0]
                                second_arg = node.targets[0].slice.dims[1]

                            first_index_l  = astu.unparse( \
                                first_arg.lower).strip('\n')

                            first_index_u  = astu.unparse( \
                                first_arg.upper).strip('\n')

                            second_index_l = astu.unparse( \
                                second_arg.lower).strip('\n')

                            second_index_u = astu.unparse( \
                                second_arg.upper).strip('\n')

                            # check if subscripted expression is used in the value
                            if hasattr(node.value, 'slice'):
                                if sys.version_info >= (3, 9):
                                    first_arg_value = node.value.slice.elts[0]
                                    second_arg_value = node.value.slice.elts[1]
                                else:
                                    first_arg_value = node.value.slice.dims[0]
                                    second_arg_value = node.value.slice.dims[1]

                                first_index_value_l  = astu.unparse( \
                                    first_arg_value.lower).strip('\n')

                                first_index_value_u  = astu.unparse( \
                                    first_arg_value.upper).strip('\n')

                                second_index_value_l = astu.unparse( \
                                    second_arg_value.lower).strip('\n')

                                second_index_value_u = astu.unparse( \
                                    second_arg_value.upper).strip('\n')

                                ai = first_index_value_l
                                aj = second_index_value_l
                                value = node.value.value.id
                            else:
                                ai = '0'
                                aj = '0'
                                value = node.value.id
                            m = first_index_u + '-' + first_index_l
                            n = second_index_u + '-' + second_index_l
                            bi = second_index_l
                            bj = second_index_l
                            self.statement([], 'c_pmt_gecp(', m, ', ', n, ', ', value, \
                                ', ', ai, ', ', aj, ', ', target, ', ', bi, ', ', bj, ');')
                        else:
                            slice_target = get_slice_value(node.targets[0].slice)

                            if not my_isinstance(slice_target, ast.Tuple):
                                # ap.pprint(node)
                                raise cgenException('Subscript to a pmat object'  
                                    'must be of type Tuple.', node.lineno)

                            # unparse slice expression
                            first_index = astu.unparse(slice_target.elts[0]).strip('\n')
                            second_index = astu.unparse(slice_target.elts[1]).strip('\n')

                            # check if subscripted expression is used in the value
                            if my_isinstance(node.value, ast.Subscript):
                                # if value is a pmat
                                value = node.value.value.id
                                if value in self.typed_record[scope]:
                                    if self.typed_record[scope][value] == 'pmat':
                                        slice_value = get_slice_value(node.value.slice)
                                        first_index_value = astu.unparse(slice_value.elts[0]).strip('\n')
                                        second_index_value = astu.unparse(slice_value.elts[1]).strip('\n')

                                        value_expr = 'c_pmt_pmat_get_el(' + value \
                                            + ', {}, {})'.format(first_index_value, \
                                            second_index_value)

                                        self.statement([], 'c_pmt_pmat_set_el(', \
                                            target, ', {}'.format(first_index), ', \
                                            {}'.format(second_index), ', {}'.format( \
                                            value_expr), ');')

                                    elif self.typed_record[scope][value] == 'pvec':
                                        # if value is a pvec
                                        slice_value = get_slice_value(node.value.slice)
                                        sub_type = type(slice_value)
                                        if sub_type in (ast.Num, ast.Constant):
                                            index_value = slice_value.n
                                        elif sub_type == ast.Name:
                                            index_value = slice_value.id
                                        else:
                                            raise cgenException('Subscripting \
                                                with value of type {} not \
                                                implemented.'.format(sub_type), \
                                                node.lineno)

                                        value_expr = 'c_pmt_pvec_get_el(' + value + \
                                            ', {})'.format(index_value)
                                        self.statement([], 'c_pmt_pmat_set_el(', \
                                            target, ', {}'.format(first_index), ', \
                                            {}'.format(second_index), ', {}'.format(value_expr), ');')
                                else:
                                    raise cgenException('Undefined variable {}.'.format(value), node.lineno)
                            else:
                                if not check_expression(node.value, tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                                        tuple([ast.USub]), ('dims'), tuple([ast.Num, ast.Constant, ast.Name]), self.dim_record):
                                    raise cgenException('Invalid value {}'.format(astu.unparse(node.value)), node.lineno)
                                value = astu.unparse(node.value)
                                self.statement([], 'c_pmt_pmat_set_el(', target, ', {}'.format(first_index), ', {}'.format(second_index), ', {}'.format(value), ');')
                        return

                    # check for pvec
                    elif self.typed_record[self.scope][target] in ('pvec'):
                        slice_target = get_slice_value(node.targets[0].slice)
                        if type(slice_target) not in (ast.Num, ast.Constant, ast.Name):
                            # ap.pprint(node)
                            raise cgenException('Subscript to a pvec must \
                                object must be of type Num or Name.', node.lineno)
                        target = node.targets[0].value.id
                        if target in self.typed_record[self.scope]:
                            # map subscript for pvec to blasfeo el assign
                            if self.typed_record[self.scope][target] in ('pvec'):
                                target = node.targets[0]
                                sub_type = type(slice_target)
                                if sub_type in (ast.Num, ast.Constant):
                                    index = slice_target.n
                                elif sub_type == ast.Name:
                                    index = slice_target.id
                                else:
                                    raise cgenException('Subscripting with \
                                        value of type {} not implemented'.format(sub_type), node.lineno)

                                # check if subscripted expression is used in the value
                                if type(node.value) == ast.Subscript:
                                    # if value is a pmat
                                    value = node.value.value.id
                                    if value in self.typed_record[self.scope]:
                                        if self.typed_record[self.scope][value] == 'pmat':
                                            slice_value = get_slice_value(node.value.slice)
                                            first_index_value = Num_or_Name(slice_value.elts[0])
                                            second_index_value = Num_or_Name(slice_value.elts[1])
                                            value_expr = 'c_pmt_pmat_get_el(' + value + ', {}, {})'.format(first_index_value, second_index_value)
                                        # single subscripting
                                        else:
                                            value = node.value.value.id
                                            # if value is a pvec
                                            if self.typed_record[self.scope][value] == 'pvec':
                                                slice_value = get_slice_value(node.value.slice)
                                                sub_type = type(slice_value)
                                                if sub_type in (ast.Num, ast.Constant):
                                                    index_value = slice_value.n
                                                elif sub_type == ast.Name:
                                                    index_value = slice_value.id
                                                else:
                                                    raise cgenException('Subscripting \
                                                        with value of type {} not \
                                                        implemented'.format(sub_type), \
                                                        node.lineno)

                                                value_expr = 'c_pmt_pvec_get_el(' + value + ', {})'.format(index_value)
                                                self.statement([], 'c_pmt_pvec_set_el(', target.value.id, ', {}'.format(index), ', {}'.format(value_expr), ');')
                                else:
                                    target = node.targets[0].value.id
                                    value = Num_or_Name(node.value)
                                    self.statement([], 'c_pmt_pvec_set_el(', target, ', {}'.format(index), ', {}'.format(value), ');')
                                return

            elif type(node.value) == ast.Subscript:
                target = node.targets[0].id
                if target not in self.typed_record[self.scope]:
                    raise cgenException('Undefined variable {}.'.format(target), node.lineno)
                # target must be a float
                if self.typed_record[self.scope][target] != 'float':

                    raise cgenException('Target must be a float {}.'.format(target), node.lineno)
                value = node.value.value.id
                if value in self.typed_record[self.scope]:
                    # if value is a pmat
                    if self.typed_record[self.scope][value] == 'pmat':
                        slice_value = get_slice_value(node.value.slice)
                        first_index_value = Num_or_Name(slice_value.elts[0])
                        second_index_value = Num_or_Name(slice_value.elts[1])
                        value_expr = 'c_pmt_pmat_get_el(' + value + ', {}, {})'.format(first_index_value, second_index_value)
                        self.statement([], target, ' = {}'.format(value_expr), ';')
                        return
                    # single subscripting
                    else:
                        # if value is a pvec
                        if self.typed_record[self.scope][value] == 'pvec':
                            slice_value = get_slice_value(node.value.slice)
                            sub_type = type(slice_value)
                            if sub_type in (ast.Num, ast.Constant):
                                index_value = slice_value.n
                            elif sub_type == ast.Name:
                                index_value = slice_value.id
                            else:
                                raise cgenException('Subscripting with value \
                                    of type {} not implemented.'.format(sub_type), \
                                    node.lineno)

                            value_expr = 'c_pmt_pvec_get_el(' + value + ', {})'.format(index_value)
                            self.statement([], target, ' = {}'.format(value_expr), ';')
                            return
            elif 'id' in node.targets[0].__dict__:

                # check for Assigns targeting pmats
                target = node.targets[0].id
                # print(target)
                if target in self.typed_record[self.scope]:
                    if self.typed_record[self.scope][target] == 'pmat':
                        if type(node.value) == ast.BinOp:
                            right_op = node.value.right.id
                            left_op = node.value.left.id
                            if right_op in self.typed_record[self.scope] and left_op in self.typed_record[self.scope]:
                                if self.typed_record[self.scope][left_op] == 'pmat' and self.typed_record[self.scope][right_op] == 'pmat':
                                    # dgemm
                                    if type(node.value.op) == ast.Mult:
                                        # set target to zero
                                        self.statement([], 'c_pmt_pmat_fill(', target, ', 0.0);')
                                        # call dgemm
                                        self.statement([], 'c_pmt_gemm_nn(', left_op, ', ', right_op, ', ', target, ', ', target, ');')
                                        return
                                    # dgead
                                    if type(node.value.op) == ast.Add:
                                        # set target to zero
                                        self.statement([], 'c_pmt_pmat_copy(', right_op, ', ', target, ');')
                                        # call dgead
                                        self.statement([], 'c_pmt_gead(1.0, ', left_op, ', ', target, ');')
                                        return
                                    # dgead (Sub)
                                    if type(node.value.op) == ast.Sub:
                                        # set target to zero
                                        self.statement([], 'c_pmt_pmat_copy(', left_op, ', ', target, ');')
                                        # call dgead
                                        self.statement([], 'c_pmt_gead(-1.0, ', right_op, ', ', target, ');')
                                        return
                                    else:
                                        raise cgenException('Unsupported operator call:{} {} {}.'\
                                            .format(self.typed_record[self.scope][left_op], \
                                            node.value.op, \
                                            self.typed_record[self.scope][right_op]), \
                                            node.lineno)

                            # elif self.typed_record[self.scope][node.value] == 'float':
                            #     value = Num_or_Name(node.value)
                            #     self.statement([], 'c_pmt_pmat_set_el(', target.value.id, ', {}'.format(first_index), ', {}'.format(second_index), ', {}'.format(value_expr), ');')


                    elif self.typed_record[self.scope][target] == 'pvec':
                        if type(node.value) == ast.BinOp:
                            right_op = node.value.right.id
                            left_op = node.value.left.id
                            if right_op in self.typed_record[self.scope] and left_op in self.typed_record[self.scope]:
                                if self.typed_record[self.scope][left_op] == 'pmat' and self.typed_record[self.scope][right_op] == 'pvec':
                                    # dgemv
                                    if type(node.value.op) == ast.Mult:
                                        # set target to zero
                                        self.statement([], 'c_pmt_pvec_fill(', target, ', 0.0);')
                                        # call dgemm
                                        self.statement([], 'c_pmt_gemv_n(', left_op, ', ', right_op, ', ', target, ', ', target, ');')
                                        return
                                    # dgead
                                    else:
                                        raise cgenException('Unsupported operator call:{} {} {}.'\
                                            .format(self.typed_record[self.scope][left_op], \
                                            node.value.op, self.typed_record[self.scope][right_op]), \
                                            node.lineno)


            elif my_isinstance(node.targets[0], ast.Attribute):
                print('CHECK THIS')
                # Assign targeting a user-defined class (C struct)
                struct_name = node.targets[0].value.id
                code = recurse_attributes(node.targets[0])
                if struct_name in self.typed_record[self.scope]:
                    attr_value = node.value.n
                    attr_name = node.targets[0].attr
                    self.statement([], struct_name, '->', attr_name, ' = ', str(attr_value), ';')
                else:
                    raise cgenException('Unknown variable {}.'.format(struct_name), node.lineno)
                return

            else:
                raise cgenException('Could not resolve Assign node.', node.lineno)
        else: 
            #TODO(andrea): is this necessary?
            raise cgenException('node has not attribute targets', node.lineno)

        set_precedence(node, node.value, *node.targets)
        self.newline(node)
        for target in node.targets:
            self.write(target, ' = ', dest = 'src')
        self.visit(node.value)
        self.write(';', dest = 'src')

    def visit_AugAssign(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.value, node.target)
        self.statement(node, node.target, get_op_symbol(node.op, ' %s= '),
                       node.value)

    def visit_AnnAssign(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        # ap.pprint(node)
        set_precedence(node, node.target, node.annotation)
        set_precedence(Precedence.Comma, node.value)
        need_parens = my_isinstance(node.target, ast.Name) and not node.simple
        begin = '(' if need_parens else ''
        end = ')' if need_parens else ''

        if 'value' not in node.__dict__:
            raise cgenException('Cannot declare variable without initialization.', node.lineno)

        ann = node.annotation.id
        # check for attributes
        if hasattr(node.target, 'value'):
            if my_isinstance(node.target, ast.Attribute):
            # if hasattr(node.target.value, 'attr'):
                if node.target.value.id != 'self' and node.target.attr not in self.typed_record[self.scope]:
                    raise cgenException('Unknown variable {}.'.format( \
                        node.target.attr), node.lineno)
                # TODO(andrea): need to handle attributes recursively
                target = node.target.attr
                obj_name = node.target.value.id
                # TODO(andrea): need to compute local scope (find strings 
                # that contain scope and have a string in common with self.scope)
                # this assumes that the class has been defined in the global scope

                # do not update scope if an instance attribute is being defined
                if node.target.value.id != 'self':
                    scope = 'global@' + self.typed_record[self.scope][obj_name]
            else:
                if node.target.value.id not in self.typed_record[self.scope]:
                    raise cgenException('variable {} already defined.'.format(node.target.value.id), node.lineno)

                target = node.target.value.id
                scope = self.scope
        else:
            target = node.target.id
            if target in self.typed_record[self.scope]:
                raise cgenException('variable {} already defined.'.format(node.target.id), node.lineno)
        # check if a CasADi function is being declared (and skip)
        if ann == 'ca':
            node_struct = {\
                'value': {\
                    'func': {'attr': {}, 'value' : {'attr': {}, 'value' : {'id' : {}}}}\
                }\
            }

            res = check_node_structure(node, node_struct)
            if res is False:
                raise cgenException('Invalid node structure. CasADi function declaration \
                    requires \n\n{}\n'.format(node_struct), node.lineno)
            
            if node.value.func.value.value.id != 'ca' or \
                    node.value.func.value.attr != 'SX' or \
                    node.value.func.attr != 'sym':
                raise cgenException('CasADi variables can only be declared calling' 
                    ' the ca.SX.sym(<name>, n, m) constructor.', node.lineno)

            return

        elif ann == 'pfun':
            # code = astu.unparse(node)
            # exec('from prometeo import * \n' + code)
            if my_isinstance(node.value, ast.Call):
                self.scope = self.scope + '@' + node.value.args[0].s
                casadi_fun = ca.Function.load('__pmt_cache__/' + self.scope + '.casadi')
                # self.function_record[outer_scope][fun_name_m] = {"arg_types": arg_list,  "ret_type": return_type_py}
                self.casadi_funs.append(self.scope)
                self.typed_record[self.scope] = dict()
                self.var_dim_record[self.scope] = dict()
                self.heap8_record[self.scope] = '0'
                self.heap64_record[self.scope] = '0'
                self.scope = descope(self.scope, '@' + node.value.args[0].s)
            else:
                raise cgenException('pfun annotation must be used to define a CasADi function' 
                        'calling the pfun constructor', node.lineno)
            return

        # check if a List is being declared
        if ann == 'List':
            if node.value.func.id != 'plist':
                raise cgenException('Cannot create Lists without using \
                    plist constructor.', node.lineno)

            if len(node.value.args) != 2:
                raise cgenException('plist constructor takes 2 arguments \
                    plist(<type>, <sizes>).', node.lineno)

            # attribute is a List
            lann = node.value.args[0].value
            dims = Num_or_Name(node.value.args[1])
            if my_isinstance(dims, str):
                self.typed_record[self.scope][target] = 'List[' + lann + ', ' + dims + ']'
            else:
                self.typed_record[self.scope][target] = 'List[' + lann + ', ' + str(dims) + ']'
            if  lann in pmt_temp_types:
                lann = pmt_temp_types[lann]
            else:
                raise cgenException ('Usage of non existing type {}.'.format(lann), node.lineno)

            # check if dims is not a numerical value
            if my_isinstance(dims, str):
                dim_list = self.dim_record[dims]
                if my_isinstance(dim_list, list):
                    array_size = len(dim_list)
                else:
                    array_size = dim_list
            else:
                array_size = dims


            # assume that AnnAssigns on attributes are only used to declare instance attributes
            if not my_isinstance(node.target, ast.Attribute):
                self.write('%s' %lann, ' ', '%s' %target, '[%s' %array_size, '];\n', dest = 'src')


            # assume that AnnAssigns on attributes are only used to declare instance attributes
            if my_isinstance(node.target, ast.Attribute):
                mod_target = 'self->' + target
            else:
                mod_target = target
            if lann == 'struct pmat *':
                # build init for List of pmats
                for i in range(len(dim_list)):
                    self.statement([], mod_target, \
                        '[', str(i),'] = c_pmt_create_pmat(', \
                        str(dim_list[i][0]), ', ', \
                        str(dim_list[i][1]), ');')

            elif lann == 'struct pvec *':
                # build init for List of pvecs
                for i in range(len(dim_list)):
                    self.statement([], mod_target, \
                        '[', str(i),'] = c_pmt_create_pvec(', \
                        str(dim_list[i][0]), ');')

        # pmat[<n>,<m>]
        elif ann == 'pmat':
            if node.value.func.id != 'pmat':
                raise cgenException('pmat objects need to be declared calling' 
                    ' the pmat(<n>, <m>) constructor.', node.lineno)

            if not check_expression(node.value.args[0], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                raise cgenException('Invalid dimension expression in pmat constructor ({})'.format(astu.unparse(node.value.args[0])), node.lineno)

            if not check_expression(node.value.args[1], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                raise cgenException('Invalid dimension expression in pmat constructor ({})'.format(astu.unparse(node.value.args[1])), node.lineno)

            dim1 = astu.unparse(node.value.args[0]).replace('\n','')
            dim2 = astu.unparse(node.value.args[1]).replace('\n','')

            # value = astu.unparse(node.value)
            self.var_dim_record[self.scope][target] = [dim1, dim2]
            node.annotation.id = pmt_temp_types[ann]
            # assume that AnnAssigns on attributes are only used to declare instance attributes
            if my_isinstance(node.target, ast.Attribute):
                self.write('\nself->' + str(node.target.attr) + ' = ', node.value, '\n', dest = 'src') 
            else:
                self.statement(node, node.annotation, ' ', node.target)
                self.conditional_write(' = ', node.value, '', dest = 'src')

            # increment scoped heap usage (3 pointers and 6 ints for pmats)
            self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                '+' + '3*' + str(self.size_of_pointer).replace('\n','')
            self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                '+' + '6*' + str(self.size_of_int).replace('\n','')

            # upper bound of blasfeo_dmat memsize
            # memsize \leq (ps + m -1)*(nc + n - 1) + (m + n + ps*nc -1)
            mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)* ' \
                '(' + str(self.blasfeo_nc) + '+' + dim2 + ' - 1)+(' + dim1 + '+' + dim2 + '+' + \
                str(self.blasfeo_ps) + '*' + str(self.blasfeo_nc) + ' - 1)'

            self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

        # or pvec[<n>]
        elif ann == 'pvec':
            if node.value.func.id != 'pvec':
                raise cgenException('pvec objects need to be declared calling the pvec(<n>, <m>) constructor.', node.lineno)

            if not check_expression(node.value.args[0], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]),
                tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                raise cgenException('Invalid dimension expression in pvec constructor ({})'.format(node.value.args[0]), self.lineno)

            dim1 = astu.unparse(node.value.args[0]).replace('\n','')
            self.var_dim_record[self.scope][node.target.id] = [dim1]
            node.annotation.id = pmt_temp_types[ann]

            # assume that AnnAssigns on attributes are only used to declare instance attributes
            if my_isinstance(node.target, ast.Attribute):
                self.write('\nself->' + str(node.target.attr) + ' = ', node.value, '\n', dest = 'src') 
            else:
                self.statement(node, node.annotation, ' ', node.target)
                self.conditional_write(' = ', node.value, '', dest = 'src')

            # increment scoped heap usage (2 pointers and 3 ints for pvecs)
            self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                '+' + '2*' + str(self.size_of_pointer).replace('\n','')
            self.heap8_record[self.scope] = self.heap8_record[self.scope] + \
                '+' + '3*' + str(self.size_of_int).replace('\n','')

            # upper bound of blasfeo_dvec memsize
            # memsize \leq ps + m -1
            mem_upper_bound = '(' + str(self.blasfeo_ps) + '+' + dim1 + ' - 1)'

            self.heap64_record[self.scope] = self.heap64_record[self.scope] + \
                '+ (' + mem_upper_bound + ' + 64)*' + str(self.size_of_double).replace('\n','')

        # or dims
        elif ann == 'dims':
            if not check_expression(node.value, tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]), \
                    tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                raise cgenException('Invalid expression for dimension', self.lineno)

            dim_value = astu.unparse(node.value).replace('\n','')
            self.write('#define %s %s\n' %(node.target.id, dim_value), dest='hdr')
            self.dim_record[node.target.id] = dim_value
            # self.write('const int %s = %s;\n' %(node.target.id, node.value.n), dest='hdr')

        # or dimv
        elif ann == 'dimv':
            self.dim_record
            self.dim_record[node.target.id] = []
            for i in range(len(node.value.elts)):
                self.dim_record[node.target.id].append([])
                for j in range(len(node.value.elts[i].elts)):
                    if not check_expression(node.value.elts[i].elts[j], tuple([ast.Mult, ast.Sub, ast.Pow, ast.Add]), \
                            tuple([ast.USub]),('dims'), tuple([ast.Num, ast.Constant]), self.dim_record):
                        raise cgenException('Invalid expression for dimension', self.lineno)

                    dim_value = astu.unparse(node.value.elts[i].elts[j]).replace('\n','')
                    self.dim_record[node.target.id][i].append(dim_value)
                    self.write('#define %s_%s_%s %s\n' %(node.target.id, i, j, dim_value), dest='hdr')

        # check if annotation corresponds to user-defined class name
        elif ann in usr_temp_types:
            class_name = node.annotation.id
            node.annotation.id = usr_temp_types[ann]
            # assume that AnnAssigns on attributes are only used to declare instance attributes
            if my_isinstance(node.target, ast.Attribute):
                self.statement([], 'self->', node.target.attr, '= & ', node.target, '___;')
                self.statement([], class_name, '_constructor(', node.target, '); //')
            else:
                self.statement([], 'struct ', class_name, ' ', node.target, '___;')
                self.statement(node, node.annotation, ' ', node.target, '= &', node.target, '___;')
                self.statement([], class_name, '_constructor(', node.target, '); //')
        else:
            if  ann in pmt_temp_types:
                c_ann = pmt_temp_types[ann]
                if my_isinstance(node.target, ast.Attribute): 
                    # annotated assign that defined an attribute (i.e. <self>.<attr_name> : <type> = <value>)
                    if node.target.value.id != 'self':
                        raise cgenException('invalid AnnAssign on attribute. AnnAssign on attributes can only be used to '
                            'define instance attributes', self.lineno)
                    else:
                        if my_isinstance(node.value, ast.Name):
                            if node.value.id not in self.typed_record:
                                raise cgenException('Unknown variable {}.'.format(node.value.id), node.lineno)
                        attr_value = Num_or_Name(node.value)
                        attr_name = node.target.attr 
                        self.statement([], node.target.value.id, '->', attr_name, ' = ', str(attr_value), ';')

                else:
                    self.statement(node, c_ann, ' ', node.target.id)
                    self.conditional_write(' = ', node.value, ';', dest = 'src')
            else:
                raise cgenException('\033[;1mUsage of non existing type\033[0;0m'
                    ' \033[1;31m{}\033[0;0m.'.format(ann), node.lineno)

        # print('typed_record = \n', self.typed_record, '\n\n')
        # print('var_dim_record = \n', self.var_dim_record, '\n\n')

        # AnnAssigns on attributes are only supported for instance attributes
        if not my_isinstance(node.target, ast.Attribute): 
            self.typed_record[self.scope][node.target.id] = ann

        # # switch to avoid double ';'
        # if type(node.value) != ast.Call:
        #     if node.value is not None:
        #         self.conditional_write(' = ', node.value, ';', dest = 'src')
        #     else:
        #         self.conditional_write(';', dest = 'src')
        # else:
        #     if node.value is not None:
        #         self.conditional_write(' = ', node.value, '', dest = 'src')
        #     else:
        #         self.conditional_write('', dest = 'src')

    def visit_ImportFrom(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        include = node.module
        include = include.replace('.','/')
        if node.level != 0:
            raise cgenException('Imports with level > 0 are not supported. Exiting.', node.lineno)
        if len(node.names) != 1:
            raise cgenException('Imports with multiple names are not supported (yet). Exiting.', node.lineno)

        if node.names[0].name != '*':
            raise cgenException('Can only transpile imports of the form: `from <...> import *`. Exiting.', node.lineno)
        self.statement(node, '#include "',
                       include or '', '.h"\n')

    def visit_Import(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        raise cgenException('Unsupported import statement. Use instead from `<...> import *` Exiting.', node.lineno)
        # self.statement(node, 'import ')
        # self.comma_list(node.names)

    def visit_Expr(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        if type(node.value) is ast.Call:
            if 'value' in node.value.func.__dict__:
                var_name = node.value.func.value.id
                # check if we are calling a method on a pmat object
                if var_name in self.typed_record[self.scope]:
                    if self.typed_record[self.scope][var_name] == 'pmat':
                        fun_name = node.value.func.attr
                        # add prefix to function call
                        node.value.func.attr = 'c_pmt_pmat_' + fun_name
        set_precedence(node, node.value)

        self.statement(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node, is_async=False):
        self.current_line = node.lineno
        self.current_col = node.col_offset

        returns = self.get_returns(node)
        if node.name == 'main':
            if returns.id != 'int':
                raise cgenException('Main must return an int', node.lineno)
            self.in_main = True
            fun_name = node.name
            fun_name_m = fun_name
        else:
            fun_name = node.name
            pre_mangl = '_Z' + str(len(fun_name))
            post_mangl = self.build_arg_mangling(node.args)
            fun_name_m = pre_mangl + fun_name + post_mangl
        # ap.pprint(node)
        # save current scope (needed to update log)
        outer_scope = self.scope

        if not outer_scope in self.function_record:
            self.function_record[outer_scope] = dict()

        self.scope = self.scope + '@' + fun_name_m
        self.typed_record[self.scope] = dict()
        self.var_dim_record[self.scope] = dict()
        self.heap8_record[self.scope] = '0'
        self.heap64_record[self.scope] = '0'
        prefix = 'is_async ' if is_async else ''
        self.decorators(node, 1 if self.indentation else 2)
        # self.write()
        if returns is None:
            raise cgenException('Missing return annotation on method {}'.format(\
                fun_name), node.lineno)

        if my_isinstance(returns, ast.NameConstant):
            return_type_py = str(returns.value)
        elif my_isinstance(returns, ast.Name):
            return_type_py = returns.id
        else:
            raise cgenException('Unknown return object {}.'.format(returns), node.lineno)

        # print(return_type_py)
        return_type_c = pmt_temp_types[return_type_py]
        # function declaration
        self.write(return_type_c, ' %s' %(fun_name_m), '(', dest = 'hdr')
        arg_list = self.visit_arguments(node.args, 'hdr')

        if not self.in_main:
            self.function_record[outer_scope][fun_name_m] = {"arg_types": arg_list,  "ret_type": return_type_py}
        
        self.write(');\n', dest = 'hdr')
        # function definition
        self.write(return_type_c, ' %s' %(fun_name_m), '(', dest = 'src')
        self.visit_arguments(node.args, 'src')
        self.write(') {\n', dest = 'src')
        if node.name == 'main':
            self.write('    prometeo_timer timer0, timer1;\n', dest = 'src')
            self.write('    double total_time, execution_time;\n', dest = 'src')
            self.write('    prometeo_tic(&timer0);\n', dest = 'src')
            self.write('    ___c_pmt_8_heap = malloc(HEAP8_SIZE); \n', dest = 'src')
            self.write('    ___c_pmt_8_heap_head = ___c_pmt_8_heap;\n', dest = 'src')
            self.write('    char * pmem_ptr = (char *)___c_pmt_8_heap;\n', dest = 'src')
            self.write('    align_char_to(8, &pmem_ptr);\n', dest = 'src')
            self.write('    ___c_pmt_8_heap = pmem_ptr;\n', dest = 'src')

            self.write('    ___c_pmt_64_heap = malloc(HEAP64_SIZE);\n', dest = 'src')
            self.write('    ___c_pmt_64_heap_head = ___c_pmt_64_heap;\n', dest = 'src')
            self.write('    pmem_ptr = (char *)___c_pmt_64_heap;\n', dest = 'src')
            self.write('    align_char_to(64, &pmem_ptr);\n', dest = 'src')
            self.write('    ___c_pmt_64_heap = pmem_ptr;\n', dest = 'src')
            self.write('    prometeo_tic(&timer1);\n', dest = 'src')

        # store current pmt_heap value (and restore before returning)
        self.write('\tvoid *callee_pmt_8_heap = ___c_pmt_8_heap;\n', dest = 'src')
        self.write('\tvoid *callee_pmt_64_heap = ___c_pmt_64_heap;\n', dest = 'src')

        # self.write(':')
        self.body(node.body)
        self.newline(1)
        if node.name == 'main':
            self.write('\texecution_time = prometeo_toc(&timer1);\n', dest='src')
            self.write('\tprintf(\"execution time:%fs\\n\", execution_time);\n', dest='src')
            self.write('\tfree(___c_pmt_8_heap_head);\n', dest='src')
            self.write('\tfree(___c_pmt_64_heap_head);\n', dest='src')
            self.write('\ttotal_time = prometeo_toc(&timer0);\n', dest='src')
            self.write('\tprintf(\"total time:%fs", total_time);\n', dest='src')
            self.write('\treturn 0;\n', dest='src')
        self.write('}', dest='src')
        if not self.indentation:
            self.newline(extra=2)
        self.scope = descope(self.scope, '@' + fun_name_m)
        self.in_main = False

    # introduced in Python 3.5
    def visit_AsyncFunctionDef(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.visit_FunctionDef(node, is_async=True)

    def visit_ClassDef(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.constructor_record.append(self.scope + '@_Z' + str(len(node.name)) + node.name)
        self.scope = self.scope + '@' + node.name
        self.typed_record[self.scope] = dict()
        self.meta_info[self.scope] = dict()
        self.var_dim_record[self.scope] = dict()
        self.heap8_record[self.scope] = '0'
        self.heap64_record[self.scope] = '0'
        have_args = []

        def paren_or_comma():
            if have_args:
                self.write(', ')
            else:
                have_args.append(True)
                self.write('(')

        # add new type to templated types
        usr_temp_types[node.name] = 'struct ' + node.name + ' *'

        self.decorators(node, 0)
        self.write('typedef struct %s %s;\n\n' %(node.name, node.name), dest = 'hdr')
        self.write('struct %s' %node.name, dest = 'hdr')

        for base in node.bases:
            self.write(paren_or_comma, base)

        # keywords not available in early version
        for keyword in self.get_keywords(node):
            self.write(paren_or_comma, keyword.arg or '',
                       '=' if keyword.arg else '**', keyword.value)
        self.conditional_write(paren_or_comma, '*', self.get_starargs(node), dest = 'src')
        self.conditional_write(paren_or_comma, '**', self.get_kwargs(node), dest = 'src')

        self.write(have_args and ')' or '', dest = 'src')
        self.write('{\n', dest = 'hdr')

        self.body_class(node.body, node.name)

        self.scope = descope(self.scope, '@' + node.name)


    def visit_If(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.test)
        self.statement(node, 'if(', node.test, ') {')
        self.body(node.body)
        while True:
            else_ = node.orelse
            if len(else_) == 1 and my_isinstance(else_[0], ast.If):
                node = else_[0]
                set_precedence(node, node.test)
                self.write('\n', '} else if (', node.test, ') {', dest='src')
                self.body(node.body)
            else:
                self.else_body(else_)
                break
        self.write('\n}', dest = 'src')

    def visit_For(self, node, is_async=False):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.target)
        prefix = 'is_async ' if is_async else ''
        if len(node.iter.args) == 1:
            # range(<value>)
            range_value = astu.unparse(node.iter.args[0]).strip('\n')
            self.statement(node, 'for(int ',
                    node.target, ' = 0; ', node.target,
                    ' < {}'.format(range_value),
                    '; ',node.target, '++) {')
        elif len(node.iter.args) == 2:
            # range(<value>, <value>)
            range_value_1 = astu.unparse(node.iter.args[0]).strip('\n')
            range_value_2 = astu.unparse(node.iter.args[1]).strip('\n')
            increment = 1
            self.statement(node, 'for(int ',
                    node.target, ' = {}; '.format(range_value_1), node.target,
                    ' < {}'.format(range_value_2),
                    '; ',node.target, '+={})'.format(increment), ' {')
        else:
            raise cgenException('Too many arguments for range().', node.lineno)

        self.body_or_else(node)
        self.write('\n    }\n', dest = 'src')

    # introduced in Python 3.5
    def visit_AsyncFor(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.visit_For(node, is_async=True)

    def visit_While(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.test)
        self.statement(node, 'while(', node.test, ') {')
        self.body_or_else(node)
        self.write('\n    }\n', dest = 'src')


    def visit_With(self, node, is_async=False):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        prefix = 'is_async ' if is_async else ''
        self.statement(node, '%swith ' % prefix)
        if hasattr(node, 'context_expr'):  # Python < 3.3
            self.visit_withitem(node)
        else:                              # Python >= 3.3
            self.comma_list(node.items)
        self.write(':')
        self.body(node.body)

    # new for Python 3.5
    def visit_AsyncWith(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.visit_With(node, is_async=True)

    # new for Python 3.3
    def visit_withitem(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(node.context_expr)
        self.conditional_write(' as ', node.optional_vars, dest = 'src')

    def visit_NameConstant(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(str(node.value), dest = 'src')

    def visit_Pass(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'pass')

    def visit_Print(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        # XXX: python 2.6 only
        self.statement(node, 'print ')
        values = node.values
        if node.dest is not None:
            self.write(' >> ')
            values = [node.dest] + node.values
        self.comma_list(values, not node.nl)

    def visit_Delete(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'del ')
        self.comma_list(node.targets)

    def visit_TryExcept(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'try:')
        self.body(node.body)
        self.write(*node.handlers)
        self.else_body(node.orelse)

    # new for Python 3.3
    def visit_Try(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'try:')
        self.body(node.body)
        self.write(*node.handlers)
        self.else_body(node.orelse)
        if node.finalbody:
            self.statement(node, 'finally:')
            self.body(node.finalbody)

    def visit_ExceptHandler(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'except')
        if self.conditional_write(' ', node.type, dest = 'src'):
            self.conditional_write(' as ', node.name, dest = 'src')
        self.write(':')
        self.body(node.body)

    def visit_TryFinally(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'try:')
        self.body(node.body)
        self.statement(node, 'finally:')
        self.body(node.finalbody)

    def visit_Exec(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        dicts = node.globals, node.locals
        dicts = dicts[::-1] if dicts[0] is None else dicts
        self.statement(node, 'exec ', node.body)
        self.conditional_write(' in ', dicts[0], dest = 'src')
        self.conditional_write(', ', dicts[1], dest = 'src')

    def visit_Assert(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.test, node.msg)
        self.statement(node, 'assert ', node.test)
        self.conditional_write(', ', node.msg, dest = 'src')

    def visit_Global(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'global ', ', '.join(node.names))

    def visit_Nonlocal(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'nonlocal ', ', '.join(node.names))

    def visit_Return(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.value)
        type_val, s = self.get_type_of_node(node.value, self.scope)
        class_scope = '@'.join(self.scope.split('@')[:-1])
        method_name = self.scope.split('@')[-1]
        if self.fun_in_function_record(self.scope):
            ret_ann = self.get_ret_type_from_function_record(self.scope)
        elif self.scope == 'global@main':
            ret_ann = 'int'
        elif class_scope in self.meta_info:
            if method_name in self.meta_info[class_scope]['methods']:
                ret_ann = self.meta_info[class_scope]['methods'][method_name]['return_type']
            else:
                raise cgenException('Could not find definition of method {}'.format(self.scope), node.lineno)
        else:
            raise cgenException('Could not find definition of method {}'.format(self.scope), node.lineno)

        if ret_ann != type_val:
            raise cgenException('Type mismatch in return statement: {} instead of {}'.format(type_val, ret_ann), \
                node.lineno)

        # TODO(andrea): this probably does not support
        # stuff like `return foo()`
        # TODO(andrea): need to check type of return!!

        # restore pmt_heap values
        self.write('\n\t___c_pmt_8_heap = callee_pmt_8_heap;\n', dest = 'src')
        self.write('\t___c_pmt_64_heap = callee_pmt_64_heap;\n', dest = 'src')
        if self.in_main is False:
            self.statement(node, 'return ')
            self.conditional_write('', node.value, ';', dest = 'src')

    def visit_Break(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'break')

    def visit_Continue(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.statement(node, 'continue')

    def visit_Raise(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        # XXX: Python 2.6 / 3.0 compatibility
        self.statement(node, 'raise')
        if self.conditional_write(' ', self.get_exc(node), dest = 'src'):
            self.conditional_write(' from ', node.cause, dest = 'src')
        elif self.conditional_write(' ', self.get_type(node), dest = 'src'):
            set_precedence(node, node.inst)
            self.conditional_write(', ', node.inst, dest = 'src')
            self.conditional_write(', ', node.tback, dest = 'src')

    # Expressions
    def visit_Attribute(self, node):
        # ap.pprint(node)
        self.current_line = node.lineno
        self.current_col = node.col_offset

        attr_chain = recurse_attributes(node)
        attr_list = attr_chain.split('->')
        if attr_list[0] == 'self':
            self.write(attr_chain, dest = 'src')
        else:
            # get type of outer object

            # TODO(andrea): as of now, only user-defined classes have methods. 
            # However, things like A.print(), where A is of type pmat, (rather than 
            # pmat_print(A)) would be quite useful.

            # if  self.typed_record[self.scope][attr_list[0]] in self.meta_info:
                # check type 
            type_val, arg_list = self.get_type_of_node(node, self.scope)
            code = recurse_attributes(node)
            self.write(attr_chain, dest = 'src')
            # else:
            #     raise cgenException('Accessing attribute of object {} \
            #         of unknown type.'.format(node.value), node.lineno)

    def visit_Call(self, node, len=len):
        # TODO(andrea): add arg type check
        self.current_line = node.lineno
        self.current_col = node.col_offset
        write = self.write
        want_comma = []

        def write_comma():
            if want_comma:
                # write(', ', dest = 'src')
                write(', ', dest = 'src')
            else:
                want_comma.append(True)

        # check if we are calling a CasADi function
        # print(node.func.id)
        if my_isinstance(node.func, ast.Name):
            if node.func.id in self.casadi_funs:
                import pdb; pdb.set_trace()

        # treat print separately
        if hasattr(node.func, 'id'):
            if node.func.id == 'print':
                if hasattr(node.args[0], 'op'):
                    if my_isinstance(node.args[0].op, ast.Mod):
                        # print string with arguments
                        write('printf("%s' %repr(node.args[0].left.s)[1:-1], '\\n", %s);\n' %node.args[0].right.id, dest = 'src')
                        return
                    else:
                        raise cgenException('Invalid operator in \
                            call to print().', node.lineno)

                else:
                    # print string with no arguments
                    write('printf("%s\\n");\n' %repr(node.args[0].s)[1:-1], dest = 'src')
                    return
            elif node.func.id == 'pparse':

                # update records
                os.chdir('__pmt_cache__')
                json_file = 'current_typed_record.json'
                with open(json_file, 'w') as f:
                    json.dump(self.typed_record[self.scope], f, indent=4, sort_keys=True)

                json_file = 'var_dim_record.json'
                with open(json_file, 'w') as f:
                    json.dump(self.var_dim_record[self.scope], f, indent=4, sort_keys=True)

                json_file = 'dim_record.json'
                with open(json_file, 'w') as f:
                    json.dump(self.dim_record, f, indent=4, sort_keys=True)

                os.chdir('..')

                expr = node.args[0].s
                # pass string to laparser
                try:
                    parser = LAParser( \
                        './__pmt_cache__/current_typed_record.json',
                        './__pmt_cache__/var_dim_record.json',
                        './__pmt_cache__/dim_record.json')
                    laparser_out = parser.parse(expr)
                except Exception as e:
                    print('\n > laparser exception: ', e)
                    raise cgenException('call to laparser failed', node.lineno)
                write(laparser_out, dest = 'src')
                return


        args = node.args
        keywords = node.keywords
        starargs = self.get_starargs(node)
        kwargs = self.get_kwargs(node)
        numargs = len(args) + len(keywords)
        numargs += starargs is not None
        numargs += kwargs is not None
        p = Precedence.Comma if numargs > 1 else Precedence.call_one_arg
        set_precedence(p, *args)

        # load function signature
        ret_type, arg_types = self.get_type_of_node(node, self.scope)
        attr = False

        if my_isinstance(node.func, ast.Name):
            fun_name = node.func.id
            f_name_len = len(fun_name)
            pre_mangl = '_Z%s' %f_name_len
            post_mangl = self.build_arg_mangling(args, is_call = True)
            fun_name_m = pre_mangl + fun_name + post_mangl

            if  fun_name_m in pmt_temp_functions:
                call_code = pmt_temp_functions[fun_name_m] + '('
            else:
                call_code = fun_name_m + '('

        elif my_isinstance(node.func, ast.Attribute):
            def get_attr_name(node):
                if hasattr(node, 'id'):
                    return node.id
                elif hasattr(node, 'value'):
                    return get_attr_name(node.value)
                else:
                    raise cgenException('Invalid call to method', node.lineno)
            attr_name = get_attr_name(node.func)
            # calling a method of a user-defined class
            attr = True
            attr_chain = recurse_attributes(node.func)
            # TODO(andrea): at some point I should mangle ANY function name
            # then mangling would move inside recurse_attributes()

            # remove unmangled function call 
            tokens = attr_chain.split('->')
            tokens = tokens[:-1]
            attr_chain = '->'.join(tokens)
            fun_name = node.func.attr
            # print(fun_name)
            # import pdb; pdb.set_trace()
            f_name_len = len(fun_name)
            pre_mangl = '_Z%s' %f_name_len
            post_mangl = self.build_arg_mangling(args, is_call = True)
            call_code = attr_chain + '->' + pre_mangl + fun_name + post_mangl + '('
            # node.func.attr = pre_mangl + fun_name + post_mangl

        if fun_name in blas_api_funs:
            call = PmtCall(fun_name)
            for arg in args:
                transpose = False
                if my_isinstance(arg, ast.Name):
                    arg_name = arg.id
                elif my_isinstance(arg, ast.Attribute):
                    if arg.attr == 'T' and self.typed_record[self.scope][arg.value.id]:
                        transpose = True
                        arg_name = arg.value.id
                this_arg = PmtArg(arg_name)
                this_arg.tran = transpose
                call.args.append(this_arg)
                call.arg_num += 1
                call.keywords = keywords
            blas_api_funs[call.name](self, call, node)
        else:
            # print(call_code)
            write(call_code, dest = 'src')
            if attr:
                write(write_comma, attr_chain, dest = 'src')

            # self.visit(node.func)

            # if my_isinstance(node.func, ast.Attribute):
            #     # calling an object's method

                        
            #     import pdb; pdb.set_trace()
            #     if len(args) > 0:
            #         code = '(' +  attr_name + ', '
            #     else:
            #         code = '(' +  attr_name
            #     write(code, dest = 'src')
            # else:
            #     write('(', dest = 'src')


            if attr:
                # TODO(andrea): assume that classes ALWAYS live in the global space? Not sure...
                fun_scope = 'global@' + self.typed_record[self.scope][attr_name]
            else:
                fun_scope = self.scope


            # if fun_scope in self.function_record:
            #     scope = self.function_record[fun_scope]
            #     if fun_name in scope:
            #         signature = scope[fun_name]
            #     elif fun_name in self.function_record['global']:
            #         signature = self.function_record['global'][fun_name]
            #     else:
            #         import pdb; pdb.set_trace()
            #         raise cgenException('Could not resolve function call "{}"'.format(fun_name), node.lineno)
            # elif fun_name in self.function_record['global']:
            #     import pdb; pdb.set_trace()
            #     signature = self.function_record['global'][fun_name]
            # else:
            #     import pdb; pdb.set_trace()
            #     raise cgenException('Could not resolve function call "{}"'.format(fun_name), node.lineno)

            if len(args) != len(arg_types):
                raise cgenException('Wrong number of arguments in call to function {}: expected {} instead of {}.'.format(\
                    fun_name, len(arg_types), len(args)), node.lineno)
            
            i = 0
            for arg in args:
                # check arg type
                if my_isinstance(arg, ast.Name):
                    arg_name = arg.id
                    if arg_name in self.typed_record[self.scope]:
                        arg_type = self.typed_record[self.scope][arg_name]
                    elif arg_name in self.typed_record['global']:
                        arg_type = self.typed_record['global'][arg_name]
                    elif arg_name in self.dim_record:
                        arg_type = self.dim_record[arg_name]
                    else:
                        raise cgenException('Could not resolve argument "{}"'.format(arg_name), node.lineno)
                elif my_isinstance(arg, "ast.Num"):
                    arg_type = type(arg.n).__name__
                else:
                    arg_type, s = self.get_type_of_node(arg, self.scope)
                    # raise cgenException('Feature not implemented: type check on arg expression.', node.lineno)

                if arg_type not in arg_types[i]:
                    raise cgenException('Argument {} has wrong type: expected {} instead of {}.'.format(i, \
                        arg_types[i], arg_type), node.lineno)

                write(write_comma, arg, dest = 'src')
                i+=1

            set_precedence(Precedence.Comma, *(x.value for x in keywords))
            for keyword in keywords:
                # a keyword.arg of None indicates dictionary unpacking
                # (Python >= 3.5)
                arg = keyword.arg or ''
                write(write_comma, arg, '=' if arg else '**', keyword.value)
            # 3.5 no longer has these
            self.conditional_write(write_comma, '*', starargs, dest = 'src')
            self.conditional_write(write_comma, '**', kwargs, dest = 'src')
            # write(');\n', dest = 'src')
            write(');', dest = 'src')

    def visit_Name(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(node.id, dest = 'src')

    def visit_JoinedStr(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.visit_Str(node, True)

    def visit_Str(self, node, is_joined=False):
        self.current_line = node.lineno
        self.current_col = node.col_offset

        # embedded is used to control when we might want
        # to use a triple-quoted string.  We determine
        # if we are in an assignment and/or in an expression
        precedence = self.get__pp(node)
        embedded = ((precedence > Precedence.Expr) +
                    (precedence >= Precedence.Assign))

        # Flush any pending newlines, because we're about
        # to severely abuse the result.source list.
        self.write('', dest = 'src')
        # result.source = self.result.source

        # Calculate the string representing the line
        # we are working on, up to but not including
        # the string we are adding.

        res_index, str_index = self.colinfo
        current_line = self.result.source[res_index:]
        if str_index:
            current_line[0] = current_line[0][str_index:]
        current_line = ''.join(current_line)

        if is_joined:

            # Handle new f-strings.  This is a bit complicated, because
            # the tree can contain subnodes that recurse back to JoinedStr
            # subnodes...

            def recurse(node):
                for value in node.values:
                    if my_isinstance(value, "ast.Str"):
                        self.write(value.s)
                    elif my_isinstance(value, ast.FormattedValue):
                        with self.delimit('{}'):
                            self.visit(value.value)
                            if value.conversion != -1:
                                self.write('!%s' % chr(value.conversion))
                            if value.format_spec is not None:
                                self.write(':')
                                recurse(value.format_spec)
                    else:
                        kind = type(value).__name__
                        assert False, 'Invalid node %s inside JoinedStr' % kind

            index = len(result.source)
            recurse(node)
            mystr = ''.join(result.source[index:])
            del result.source[index:]
            self.colinfo = res_index, str_index  # Put it back like we found it
            uni_lit = False  # No formatted byte strings

        else:
            mystr = node.s
            uni_lit = self.using_unicode_literals

        mystr = self.pretty_string(mystr, embedded, current_line, uni_lit)

        if is_joined:
            mystr = 'f' + mystr

        self.write(mystr, dest = 'src')

        lf = mystr.rfind('\n') + 1
        if lf:
            self.colinfo = len(result.source) - 1, lf

    def visit_Bytes(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(repr(node.s))

    def visit_Num(self, node,
                  # constants
                  new=sys.version_info >= (3, 0)):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node) as delimiters:
            s = repr(node.n)

            # Deal with infinities -- if detected, we can
            # generate them with 1e1000.
            signed = s.startswith('-')
            if s[signed].isalpha():
                im = s[-1] == 'j' and 'j' or ''
                assert s[signed:signed + 3] == 'inf', s
                s = '%s1e1000%s' % ('-' if signed else '', im)
            self.write(s, dest = 'src')

            # The Python 2.x compiler merges a unary minus
            # with a number.  This is a premature optimization
            # that we deal with here...
            if not new and delimiters.discard:
                if signed:
                    pow_lhs = Precedence.Pow + 1
                    delimiters.discard = delimiters.pp != pow_lhs
                else:
                    op = self.get__p_op(node)
                    delimiters.discard = not my_isinstance(op, ast.USub)

    def visit_Tuple(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node) as delimiters:
            # Two things are special about tuples:
            #   1) We cannot discard the enclosing parentheses if empty
            #   2) We need the trailing comma if only one item
            elts = node.elts
            delimiters.discard = delimiters.discard and elts
            self.comma_list(elts, len(elts) == 1)

    def visit_List(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit('[]'):
            self.comma_list(node.elts)

    def visit_Set(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit('{}'):
            self.comma_list(node.elts)

    def visit_Dict(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(Precedence.Comma, *node.values)
        with self.delimit('{}'):
            for idx, (key, value) in enumerate(zip(node.keys, node.values)):
                self.write(', ' if idx else '',
                           key if key else '',
                           ': ' if key else '**', value)

    def visit_BinOp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        op, left, right = node.op, node.left, node.right
        with self.delimit(node, op) as delimiters:
            ispow = my_isinstance(op, ast.Pow)
            p = delimiters.p
            set_precedence((Precedence.Pow + 1) if ispow else p, left)
            set_precedence(Precedence.PowRHS if ispow else (p + 1), right)
            self.write(left, get_op_symbol(op, ' %s '), right, dest = 'src')

    def visit_BoolOp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node, node.op) as delimiters:
            op = get_op_symbol(node.op, ' %s ')
            set_precedence(delimiters.p + 1, *node.values)
            for idx, value in enumerate(node.values):
                self.write(idx and op or '', value)

    def visit_Compare(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node, node.ops[0]) as delimiters:
            set_precedence(delimiters.p + 1, node.left, *node.comparators)
            self.visit(node.left)
            for op, right in zip(node.ops, node.comparators):
                self.write(get_op_symbol(op, ' %s '), right, dest = 'src')

    def visit_UnaryOp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node, node.op) as delimiters:
            set_precedence(delimiters.p, node.operand)
            # In Python 2.x, a unary negative of a literal
            # number is merged into the number itself.  This
            # bit of ugliness means it is useful to know
            # what the parent operation was...
            node.operand._p_op = node.op
            sym = get_op_symbol(node.op)
            self.write(sym, ' ' if sym.isalpha() else '', node.operand, dest = 'src')

    def visit_Subscript(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.slice)
        self.write(node.value, '[', node.slice, ']', dest = 'src')

    def visit_Slice(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.lower, node.upper, node.step)
        self.conditional_write(node.lower, dest = 'src')
        self.write(':')
        self.conditional_write(node.upper, dest = 'src')
        if node.step is not None:
            self.write(':')
            if not (my_isinstance(node.step, ast.Name) and
                    node.step.id == 'None'):
                self.visit(node.step)

    def visit_Index(self, node):
        self.current_line = node.value.lineno
        self.current_col = node.value.col_offset
        with self.delimit(node) as delimiters:
            set_precedence(delimiters.p, node.value)
            self.visit(node.value)

    def visit_ExtSlice(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        dims = node.dims
        set_precedence(node, *dims)
        self.comma_list(dims, len(dims) == 1)

    def visit_Yield(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node):
            set_precedence(get_op_precedence(node) + 1, node.value)
            self.write('yield')
            self.conditional_write(' ', node.value, dest = 'src')

    # new for Python 3.3
    def visit_YieldFrom(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node):
            self.write('yield from ', node.value)

    # new for Python 3.5
    def visit_Await(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node):
            self.write('await ', node.value)

    def visit_Lambda(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node) as delimiters:
            set_precedence(delimiters.p, node.body)
            self.write('lambda ')
            self.visit_arguments(node.args, 'src')
            self.write(': ', node.body)

    def visit_Ellipsis(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write('...')

    def visit_ListComp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit('[]'):
            self.write(node.elt, *node.generators)

    def visit_GeneratorExp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node) as delimiters:
            if delimiters.pp == Precedence.call_one_arg:
                delimiters.discard = True
            set_precedence(Precedence.Comma, node.elt)
            self.write(node.elt, *node.generators)

    def visit_SetComp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit('{}'):
            self.write(node.elt, *node.generators)

    def visit_DictComp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit('{}'):
            self.write(node.key, ': ', node.value, *node.generators)

    def visit_IfExp(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        with self.delimit(node) as delimiters:
            set_precedence(delimiters.p + 1, node.body, node.test)
            set_precedence(delimiters.p, node.orelse)
            self.write(node.body, ' if ', node.test, ' else ', node.orelse)

    def visit_Starred(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write('*', node.value)

    def visit_Repr(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        # XXX: python 2.6 only
        with self.delimit('``'):
            self.visit(node.value)

    def visit_Module(self, node):
        self.write(*node.body, dest = 'src')

    visit_Interactive = visit_Module

    def visit_Expression(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.visit(node.body)

    # Helper Nodes

    def visit_arg(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(node.arg)
        self.conditional_write(': ', node.annotation, dest = 'src')

    def visit_alias(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        self.write(node.name, dest = 'src')
        self.conditional_write(' as ', node.asname, dest = 'src')

    def visit_comprehension(self, node):
        self.current_line = node.lineno
        self.current_col = node.col_offset
        set_precedence(node, node.iter, *node.ifs)
        set_precedence(Precedence.comprehension_target, node.target)
        stmt = ' is_async for ' if self.get_is_is_async(node) else ' for '
        self.write(stmt, node.target, ' in ', node.iter)
        for if_ in node.ifs:
            self.write(' if ', if_)
