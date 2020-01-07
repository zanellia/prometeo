import ast
from collections import defaultdict
from ..cgen.node_util import ExplicitNodeVisitor
import astpretty as ap
from ..cgen.op_util import get_op_symbol, get_op_precedence, Precedence

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
    pop = '@' + pop
    if current_scope.endswith(pop):
        return current_scope[:-len(pop)]
    return current_scope

class ast_visitor(ExplicitNodeVisitor):
    def __init__(self):
        self.callees = dict() 
        self.caller_scope = 'global'
        self.callee_scope = 'global'
        self.in_call = False
        visit = self.visit

        def visit_ast(*params):
            for item in params:
                ap.pprint(item)
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
        self.caller_scope = self.caller_scope + '@' + node.name
        self.callees[self.caller_scope] = []
        # self.visit_ast(node)
        self.body(node.body)
        self.caller_scope = descope(self.caller_scope, node.name)

    def visit_ClassDef(self, node):
        self.caller_scope = self.caller_scope + '@' + node.name
        self.body(node.body)
        descope(self.caller_scope, node.name)

    def visit_Expr(self, node):
        set_precedence(node, node.value)
        self.aux_visit_ast(node)
        self.generic_visit(node)

    def visit_Expression(self, node):
        self.visit(node.body)

    def visit_Call(self, node, len=len):
        ap.pprint(node)
        if isinstance(node.func, ast.Name):
            self.callees[self.caller_scope].append(self.callee_scope + '@' + node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.in_call = True 
            self.visit(node.func)
            self.callees[self.caller_scope].append(self.callee_scope)
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
    # def get_call_graph(tree):
    # def visit_Call(self, node):
    #     self.callees.append(node.func.id)
    #     self.generic_visit(node)
# class ast_visitor(ast.NodeVisitor):
#     def __init__(self):
#         self.callees = [] 

#     def visit_Call(self, node):
#         self.callees.append(node.func.id)
#         self.generic_visit(node)


# def get_call_graph(tree):
#     call_graph = {}
#     for node in ast.walk(tree):
#         print(node)
#         import pdb; pdb.set_trace()
#         if isinstance(node, ast.FunctionDef):
#             visitor = ast_visitor()
#             visitor.visit(node)
#             call_graph[node.name] = visitor.callees

#     return call_graph 

def compute_reach_graph(tree):
    nodes = tree.keys()
    reach_map = {}
    for curr_node in nodes:
        reach_map[curr_node] = get_reach_nodes(tree, curr_node, curr_node, [], 1) 
    return reach_map

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

