# import ast
# class ast_analyzer(ast.NodeTransformer):
#     def visit_Call(self, node):
#         node_copy = node
#         # import pdb; pdb.set_trace()
#         print(node_copy.func.id)
#         if hasattr(node_copy, 'callees'):
#             if node_copy.func.id not in node_copy.callees:
#                 node_copy.callees.append(node_copy.func.id)
#                 print(node_copy.callees)
#         else:
#             node_copy.callees = [node_copy.func.id]
#             print(node_copy.callees)
#         self.generic_visit(node_copy)
#         return node_copy
'''
Get all function calls from a python file

The MIT License (MIT)
Copyright (c) 2016 Suhas S G <jargnar@gmail.com>
'''
import ast
from collections import deque


class ast_visitor(ast.NodeVisitor):
    def __init__(self):
        self.callees = [] 

    def visit_Call(self, node):
        self.callees.append(node.func.id)
        self.generic_visit(node)


def get_func_calls(tree):
    call_graph = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            visitor = ast_visitor()
            visitor.visit(node)
            call_graph[node.name] = visitor.callees

    return call_graph 
