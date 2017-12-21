import ast
import astpretty
import typing
import code_gen
import code_gen_c

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


filename = 'code.hipex'
tree = ast.parse(''.join(open(filename)))
# astpretty.pprint(tree)

c_code = code_gen_c.to_source(tree)
# print("\n", c_code)

dest_file = open('code.c', 'w')
dest_file.write(c_code)
