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
from collections import defaultdict

class ast_visitor(ast.NodeVisitor):
    def __init__(self):
        self.callees = [] 

    def visit_Call(self, node):
        self.callees.append(node.func.id)
        self.generic_visit(node)


def get_call_graph(tree):
    call_graph = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            visitor = ast_visitor()
            visitor.visit(node)
            call_graph[node.name] = visitor.callees

    return call_graph 


# class Graph():
#     def __init__(self,vertices):
#         self.graph = defaultdict(list)
#         self.V = vertices
 
#     def addEdge(self,u,v):
#         self.graph[u].append(v)
 
def isCyclicUtil(self, v, visited, recStack):

    # Mark current node as visited and 
    # adds to recursion stack
    visited[v] = True
    recStack[v] = True

    # Recur for all neighbours
    # if any neighbour is visited and in 
    # recStack then graph is cyclic
    for neighbour in self.graph[v]:
        if visited[neighbour] == False:
            if self.isCyclicUtil(neighbour, visited, recStack) == True:
                return True
        elif recStack[neighbour] == True:
            return True

    # The node needs to be poped from 
    # recursion stack before function ends
    recStack[v] = False
    return False

# Returns true if graph is cyclic else false
def isCyclic(self):
    visited = [False] * self.V
    recStack = [False] * self.V
    for node in range(self.V):
        if visited[node] == False:
            if self.isCyclicUtil(node,visited,recStack) == True:
                return True
    return False
 
# g = Graph(4)
# g.addEdge(0, 1)
# g.addEdge(0, 2)
# g.addEdge(1, 2)
# g.addEdge(2, 0)
# g.addEdge(2, 3)
# g.addEdge(3, 3)
# if g.isCyclic() == 1:
#     print "Graph has a cycle"
# else:
#     print "Graph has no cycle"
