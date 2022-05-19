import ast
from collections import defaultdict
from ..cgen.node_util import ExplicitNodeVisitor
import astpretty as ap
from ..cgen.op_util import get_op_symbol, get_op_precedence, Precedence
import json
from collections import Iterable
from copy import deepcopy

pmt_functions = {\
    'global@_Z4pmatdimsdims' : [], \
    'global@_Z4pvecdims' : [], \
    'global@_Z10pmat_printpmat' : [], \
    'global@_Z8pmt_gemmpmatpmatpmat' : [], \
    'global@_Z8pmt_gemmpmatpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_nnpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_nnpmatpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_ntpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_ntpmatpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_tnpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_tnpmatpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_ttpmatpmatpmat' : [], \
    'global@_Z11pmt_gemm_ttpmatpmatpmatpmat' : [], \
    'global@_Z8pmt_geadfloatpmatpmat' : [], \
    'global@_Z9pmt_potrfpmatpmat' : [], \
    'global@_Z10pmt_potrsmpmatpmat' : [], \
    'global@_Z9pmat_tranpmatpmat' : [], \
    'global@_Z9pmat_copypmatpmat' : [], \
    'global@_Z9pmat_fillpmatfloat' : [], \
    'global@_Z9pmat_hcatpmatpmatpmat' : [], \
    'global@_Z9pmat_vcatpmatpmatpmat' : [], \
    'global@_Z10pvec_printpvec' : [], \
    'global@_Z9pvec_copypvecpvec' : [], \
    'global@_Z5printstr' : [], \
    'global@_Z5pliststrdims' : [], \

}

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

class cgenException(Exception):
    def __init__(self, message, lineno):
        super().__init__(message)
        self.message = message
        self.lineno = lineno

def precedence_setter(AST=ast.AST, get_op_precedence=get_op_precedence,
                      isinstance=isinstance, list=list):
    """ This only uses a closure for performance reasons,
        to reduce the number of attribute lookups.  (set_precedence
        is called a lot of times.)
    """

    def set_precedence(value, *nodes):
        """Set the precedence (of the parent) into the children.
        """
        if isinstance(value, AST):
            value = get_op_precedence(value)
        for node in nodes:
            if isinstance(node, AST):
                node._pp = value
            elif isinstance(node, list):
                set_precedence(value, *node)
            else:
                assert node is None, node

    return set_precedence

set_precedence = precedence_setter()

def descope(current_scope, pop):
    if current_scope.endswith(pop):
        return current_scope[:-len(pop)]
    else:
        raise Exception('Attempt to descope {}, which is not the current scope'.format(pop))

def flatten(coll):
    for i in coll:
            if isinstance(i, Iterable) and not isinstance(i, str):
                for subc in flatten(i):
                    yield subc
            else:
                yield i

def recurse_attributes(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return recurse_attributes(node.value) + '->' + node.attr 
    else:
        raise Exception('Invalid attribute or method {}'.format(node))

class ast_visitor(ExplicitNodeVisitor):
    def __init__(self):
        self.callees = pmt_functions
        self.caller_scope = 'global'
        self.callee_scope = 'global'
        self.in_call = False
        # load local typed_record

        with open('__pmt_cache__/typed_record.json', 'r') as f:
            self.typed_record = json.load(f)

        with open('__pmt_cache__/dim_record.json', 'r') as f:
            self.dim_record = json.load(f)

        with open('__pmt_cache__/meta_info.json', 'r') as f:
            self.meta_info = json.load(f)

        visit = self.visit

        def visit_ast(*params):
            for item in params:
                # ap.pprint(item)
                if isinstance(item, ast.AST):
                    visit(item)
                elif callable(item):
                    item()

        self.visit_ast = visit_ast

    def aux_visit_ast(self, node, *params):
        self.visit_ast(*params)

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
                if type_l != 'str' or (type_r != 'int' and type_r != 'float'): # allow for this case for printing TODO : improve
                    raise Exception("Type mismatch in BinOp: left = {}, right = {}".format(type_l,type_r))
            return type_l, None

        elif my_isinstance(node, ast.UnaryOp):
            type_val, s  = self.get_type_of_node(node.operand, scope)
            return type_val, None

        elif my_isinstance(node, ast.Subscript):
            if my_isinstance(node.value, ast.Name):
                if node.value.id not in self.typed_record[scope]:
                    raise Exception('Undefined variable {}'.format(node.id))
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
                raise Exception("Invalid node type {}".format(node.value))

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
                if node.func.id not in self.function_record['global']:
                    raise cgenException('Undefined method {}'.format(node.func.id), node.lineno)
                type_val = self.function_record['global'][node.func.id]['ret_type']
                return type_val,  self.function_record['global'][node.func.id]['arg_types']

            type_val = self.get_type_of_node_rec(node.func.value, scope)

            if node.func.attr not in self.meta_info[type_val]['methods']:
                raise cgenException('Undefined method {}'.format(node.func.attr), node.lineno)
            arg_types = self.meta_info[type_val]['methods'][node.func.attr]['args']
            type_val = self.meta_info[type_val]['methods'][node.func.attr]['return_type']

            return type_val, arg_types

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
                if isinstance(arg.annotation, ast.Name):
                    arg_type_py = arg.annotation.id
                    post_mangl = post_mangl + arg_type_py
                elif arg.arg is not 'self':
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
                if isinstance(arg, ast.Num):
                    if isinstance(arg.n, int):
                        arg_value = 'int'
                    elif isinstance(arg.n, float):
                        arg_value = 'float'
                    else:
                        raise cgenException('Invalid numeric argument.\n', arg.lineno)
                    post_mangl = post_mangl + arg_value
                else:
                    # arg_value = arg.id
                    type_val, s = self.get_type_of_node(arg, self.caller_scope)
                    post_mangl = post_mangl + type_val
            return post_mangl

        if is_call:
            post_mangl = loop_args_mangl(args)
        else:
            post_mangl = loop_args_mangl_def(args.args, args.defaults)

        return post_mangl

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

    def body(self, args):
        self.visit_ast(*args)

    def visit_Module(self, node):
        self.visit_ast(*node.body)
        return

    def visit_FunctionDef(self, node):
        # if node.name != '__init__':

        fun_name = node.name
        if fun_name == 'main':
            fun_name_m = 'main'
        else:
            f_name_len = len(node.name)
            pre_mangl = '_Z%s' %f_name_len
            post_mangl = self.build_arg_mangling(node.args, is_call = False)
            fun_name_m = pre_mangl + node.name + post_mangl

        self.caller_scope = self.caller_scope + '@' + fun_name_m
        self.callees[self.caller_scope] = set([])
        # self.visit_ast(node)
        self.body(node.body)
        self.caller_scope = descope(self.caller_scope, '@' + fun_name_m)

    def visit_ClassDef(self, node):
        class_name = node.name
        class_name_m = '_Z' + str(len(class_name)) + class_name

        # register constructor
        self.callees[self.caller_scope + '@' + class_name_m] = set([])

        self.caller_scope = self.caller_scope + '@' + class_name
        self.body(node.body)
        self.caller_scope = descope(self.caller_scope, '@' + class_name)

    def visit_Expr(self, node):
        set_precedence(node, node.value)
        self.aux_visit_ast(node)
        self.generic_visit(node)

    def visit_Expression(self, node):
        self.visit(node.body)

    def resolve_call(self, node, pre_mangl, post_mangl):
        callee = self.resolve_call_rec(node.value)
        return callee + '@' + pre_mangl + node.attr + post_mangl

    def resolve_call_rec(self, node):
        if isinstance(node, ast.Name):
            return node.id
        else:
            callee = self.resolve_call_rec(node.value)
            return callee

    def visit_Call(self, node, len=len):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            func_name = node.func.attr
        f_name_len = len(func_name)
        pre_mangl = '_Z%s' %f_name_len
        post_mangl = self.build_arg_mangling(node.args, is_call = True)

        if isinstance(node.func, ast.Name):
            if func_name == 'main':
                # do not mangle function name
                self.callees[self.caller_scope].add(self.callee_scope + '@' + func_name)
            else:
                # mangle function name
                self.callees[self.caller_scope].add(self.callee_scope + '@' + pre_mangl + func_name + post_mangl)
        elif isinstance(node.func, ast.Attribute):
            callee = self.resolve_call(node.func, pre_mangl, post_mangl)
            self.callees[self.caller_scope].add(self.callee_scope + '@' + callee)
        else:
            raise Exception('Could not analyze call {}'.format(node))

    def visit_Name(self, node):
        return
        # self.generic_visit(node)

    def visit_Tuple(self, node):
        self.generic_visit(node)

    def visit_Set(self, node):
        self.generic_visit(node)

    def visit_Return(self, node):
        self.aux_visit_ast(node)

    def visit_Assign(self, node):
        set_precedence(node, node.value)
        self.visit(node.value)

    def visit_Num(self, node):
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.visit_ast(node.value)
        if self.in_call:
            if isinstance(node.value, ast.Name):
                self.callee_scope = self.callee_scope + '@' + node.value.id + '@' + node.attr
            else:
                self.callee_scope = self.callee_scope + '@' + node.attr
        return
        # self.visit_ast(node.attr)

    def visit_JoinedStr(self, node):
        return

    def visit_Str(self, node, is_joined=False):
        return

    def else_body(self, elsewhat):
        if elsewhat:
            self.body(elsewhat)

    def body_or_else(self, node):
        self.body(node.body)
        self.else_body(node.orelse)

    def visit_For(self, node, is_async=False):
        self.body_or_else(node)

    def visit_While(self, node, is_async=False):
        self.body_or_else(node)

    def visit_ImportFrom(self, node):
        return

    def visit_Import(self, node):
        return

    def visit_If(self, node):
        return

    def visit_AnnAssign(self, node):
        self.visit(node.value)
        return

    def visit_Subscript(self, node):
        return

    def visit_List(self, node):
        return

    def visit_BinOp(self, node):
        return

    def visit_UnaryOp(self, node):
        return

def merge_call_graphs(dict1, dict2):
    '''
    Merge call graphs represented by dictionaries of the form
    { <caller> : <calles> (set)}. No recursive merging.
    '''
    union_dict = deepcopy(dict1)

    for key, value in dict2.items():
        if key in union_dict:
            union_dict[key] = value.union(union_dict[key])
        else:
            union_dict[key] = value

    return union_dict

def compute_reach_graph(call_graph, typed_record, meta_info):
    """
    Compute reachability map associated with a given call graph.

    Parameters
    ----------
    call_graph : dict
        dictionary with structure { <caller> : <calles> (set)} containing
        the call graph computed inspecting the Python AST.

    typed_record : dict
        dictionary containing the meta-information extracted by prometeo's
        parser.

    meta_info : dict
        dictionary containing the meta-information extracted by prometeo's
        parser.

    Returns
    -------
    reach_map : dict
        dictionary with structure { <caller> : <reachable_methods> ([str])}
        containing the reachability map.

    call_graph : dict
        dictionary with structure { <caller> : <reachable_methods> ([str])}
        containing the call_graph with resolved calls.

    """
    # get unresolved calls
    all_methods = list(call_graph.keys())
    # calls = list(call_graph.values())
    unresolved_calls = set([])
    unresolved_callers = dict()
    graph_copy = deepcopy(call_graph)

    # note: trivial calls are not added to unresolved_callers
    for method in call_graph:
        unresolved_callers[method] = set([])
        for call in call_graph[method]:
            if call not in all_methods and call != set([]):
                # skip CasADi-related calls
                if '@ca@' not in call:
                    # add call to dictionary of unresolved calls
                    unresolved_callers[method].add(call)
                # remove call from call graph
                graph_copy[method].remove(call)


    call_graph = deepcopy(graph_copy)

    # strip empty calls
    r_unresolved_callers = dict()
    for caller in unresolved_callers:
        if unresolved_callers[caller] != set([]):
            r_unresolved_callers[caller] = unresolved_callers[caller]

    # TODO(andrea): here again, we assume that classes live in the global scope
    def resolve_scopes(call, caller, typed_record, meta_info):
        scopes = call.split('@')
        if scopes[0] != 'global':
            raise Exception('Invalid leading scope {}'.format(scopes[0]))
        if scopes[1] not in typed_record[caller]:
            raise Exception('Could not resolve scope name {}'.format(scopes[1]))
        else:
            scopes[1] = typed_record[caller][scopes[1]]

        # here assume that the last scope corresponds to a method and the others to
        # attributes
        for i in range(1,len(scopes)-2):
            if scopes[i+1] not in meta_info['global@' + scopes[i]]["attr"]:
                raise Exception('Could not resolve attribute {}'.format(scopes[i+1]))
            else:
                scopes[i+1] = meta_info['global@' + scopes[i]]["attr"][scopes[i+1]]

        return scopes

    r_resolved_callers = dict()
    # resolve non-trivial calls
    r_unresolved_callers_copy = deepcopy(r_unresolved_callers)
    for caller in r_unresolved_callers_copy:
        for call in r_unresolved_callers_copy[caller]:
            scopes = resolve_scopes(call, caller, typed_record, meta_info)
            t_call = '@'.join(scopes)
            if t_call in all_methods:
                r_unresolved_callers[caller].remove(call)
                if caller not in r_resolved_callers:
                    r_resolved_callers[caller] = set([])
                r_resolved_callers[caller].add(t_call)

    # for caller in r_unresolved_callers:
    #     for call in r_unresolved_callers[caller]:
    #         import pdb; pdb.set_trace()
    #         scopes = call.split('@')
    #         curr_scope = scopes[0]
    #         for j in range(len(scopes)-1):
    #             if curr_scope + '@' + scopes[j+1] in typed_record:
    #                 curr_scope = curr_scope + '@' + scopes[j+1]
    #             else:
    #                 # try to resolve class name
    #                 if scopes[j] in typed_record[caller]:
    #                     scopes[j] = typed_record[caller][scopes[j]]
    #                 t_call = '@'.join(scopes)
    #                 if t_call in all_methods:
    #                     r_unresolved_callers[caller].remove(call)
    #                     r_unresolved_callers[caller].add(t_call)
    #                     break

    # update call_graph with unresolved calls
    call_graph = merge_call_graphs(call_graph, r_resolved_callers)

    # check that there are no unresolved calls
    # TODO(andrea): this is a bit ugly
    unresolved_calls = set([])
    unresolved_callers = dict()
    for method in call_graph:
        unresolved_callers[method] = set([])
        graph_copy = deepcopy(call_graph)
        for call in call_graph[method]:
            if call not in all_methods and call != set([]):
                # add call to dictionary of unresolved calls
                unresolved_callers[method].add(call)
                # remove call from call graph
                graph_copy[method].remove(call)

    call_graph = deepcopy(graph_copy)

    # remove unreachable nodes from call graph
    for key_outer, value_outer in call_graph.items():
        reachable = False
        for key_inner, value_inner in call_graph.items():
            if key_outer in value_inner:
                reachable = True
        if not reachable and key_outer in graph_copy and key_outer != 'global@main':
            del graph_copy[key_outer]

    call_graph = deepcopy(graph_copy)

    # strip empty calls
    r_unresolved_callers = dict()
    for caller in unresolved_callers:
        if unresolved_callers[caller] != set([]):
            r_unresolved_callers[caller] = unresolved_callers[caller]

    if r_unresolved_callers != dict():
        raise Exception('call graph analyzer -- could not resolve the \
            following calls {}'.format(r_unresolved_callers))

    reach_map = {}
    for curr_node in call_graph:
        reach_map[curr_node] = get_reach_nodes(call_graph, curr_node, curr_node, [], 1)

    # TODO(andrea): still useful?
    # eliminate (some) unreachable nodes from reachability map
    reach_map_copy = deepcopy(reach_map)
    for n_outer_k, n_outer_v in reach_map.items():
        if n_outer_k != 'global@main':
            reachable = False
            for n_inner_k, n_inner_v in reach_map.items():
                if n_outer_k in n_inner_v:
                    reachable = True
            if not reachable:
                reach_map_copy.pop(n_outer_k)

    # convert sets to lists
    for key, value in call_graph.items():
        call_graph[key] = list(value)

    return reach_map_copy, call_graph

def get_reach_nodes(call_graph, curr_call, root, reach_nodes_h, root_flag):
    if not call_graph[curr_call] and not root_flag:
        if curr_call not in reach_nodes_h:
            reach_nodes_h += [curr_call]
        return reach_nodes_h
    else:
        if curr_call in reach_nodes_h:
            if curr_call not in reach_nodes_h:
                reach_nodes_h += [curr_call]
            return reach_nodes_h
        if root == curr_call and not root_flag:
            reach_nodes_h += ['*']
            return reach_nodes_h
        else:
            if curr_call != root:
                if curr_call not in reach_nodes_h:
                    reach_nodes_h += [curr_call]
            for call_iter in call_graph[curr_call]:
                reach_nodes_h = get_reach_nodes(call_graph, call_iter, root, reach_nodes_h, 0)
            return reach_nodes_h

