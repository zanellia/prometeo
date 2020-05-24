import ast
from collections import defaultdict
from ..cgen.node_util import ExplicitNodeVisitor
import astpretty as ap
from ..cgen.op_util import get_op_symbol, get_op_precedence, Precedence
import json
from collections import Iterable
from copy import deepcopy

pmt_functions = {\
    'global@pmat': [], \
    'global@pvec': [], \
    'global@plist': [], \
    'global@pmat_copy': [], \
    'global@pmat_print': [], \
    'global@pvec_print': [], \
    'global@pmat_fill': [], \
    'global@pmat_tran': [], \
    'global@pmat_hcat': [], \
    'global@pmat_vcat': [], \
    'global@pmt_gemm_nn': [], \
    'global@pmt_gemm_tn': [], \
    'global@pmt_gemm_nt': [], \
    'global@pmt_trmm_rlnn': [], \
    'global@pmt_syrk_ln': [], \
    'global@pmt_gead': [], \
    'global@pmt_potrf': [], \
    'global@pmt_potrsm': [], \
    'global@pmt_getrf': [], \
    'global@pmt_getrsm': [], \
    'global@print': [], \
    'global@pparse': [], \
    'global@pparse': [], \
    }

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

class ast_visitor(ExplicitNodeVisitor):
    def __init__(self):
        self.callees = pmt_functions
        self.caller_scope = 'global'
        self.callee_scope = 'global'
        self.in_call = False
        # load local typed_record

        with open('__pmt_cache__/typed_record.json', 'r') as f:
            self.typed_record = json.load(f)
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
        self.caller_scope = self.caller_scope + '@' + node.name
        self.callees[self.caller_scope] = set([])
        # self.visit_ast(node)
        self.body(node.body)
        self.caller_scope = descope(self.caller_scope, '@' + node.name)

    def visit_ClassDef(self, node):
        self.caller_scope = self.caller_scope + '@' + node.name
        self.callees[self.caller_scope] = set([])
        self.body(node.body)
        self.caller_scope = descope(self.caller_scope, '@' + node.name)

    def visit_Expr(self, node):
        set_precedence(node, node.value)
        self.aux_visit_ast(node)
        self.generic_visit(node)

    def visit_Expression(self, node):
        self.visit(node.body)

    def visit_Call(self, node, len=len):
        # ap.pprint(node)
        if isinstance(node.func, ast.Name):
            self.callees[self.caller_scope].add(self.callee_scope + '@' + node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.in_call = True
            self.visit(node.func)
            self.callees[self.caller_scope].add(self.callee_scope)
            self.in_call = False

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

def compute_reach_graph(call_graph, typed_record):
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

    # resolve calls
    for caller in r_unresolved_callers:
        for call in r_unresolved_callers[caller]:
            scopes = call.split('@')
            curr_scope = scopes[0]
            for j in range(len(scopes)-1):
                if curr_scope + '@' + scopes[j+1] in typed_record:
                    curr_scope = curr_scope + '@' + scopes[j+1]
                else:
                    # try to resolve class name
                    if scopes[j] in typed_record[caller]:
                        scopes[j] = typed_record[caller][scopes[j]]
                    t_call = '@'.join(scopes)
                    if t_call in all_methods:
                        r_unresolved_callers[caller].remove(call)
                        r_unresolved_callers[caller].add(t_call)
                        break

    # update call_graph with unresolved calls
    call_graph = merge_call_graphs(call_graph, r_unresolved_callers)

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

