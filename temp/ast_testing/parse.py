import ast
import astpretty
import typing

class v(ast.NodeVisitor):
    def generic_visit(self, node):
        print (type(node).__name__)
        ast.NodeVisitor.generic_visit(self, node)

class FuncLister(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)

def iter_all_ast(node):
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    for child in iter_all_ast(item):
                        print(child)
        elif isinstance(value, ast.AST):
            for child in iter_all_ast(value):
                print(child)


filename = 'code.py'
tree = ast.parse(''.join(open(filename)))
# astpretty.pprint(tree)
# FuncLister().visit(tree)
iter_all_ast(tree)

# v().visit(tree)

# for node in ast.walk(tree):
#     print(node)
