import prometeo
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


# filename = 'new_test'
filename = 'dgemm'
py_filename = filename + '.py'
c_filename = filename + '.c'
tree = ast.parse(''.join(open(py_filename)))
astpretty.pprint(tree)

result  = prometeo.cgen.code_gen_c.to_source(tree, filename, main=True, ___c_prmt_heap_size=100000)

print("source = \n", prometeo.cgen.source_repr.pretty_source(result.source))
print("header = \n", prometeo.cgen.source_repr.pretty_source(result.header))

dest_file = open(filename + '.c', 'w')
dest_file.write(prometeo.cgen.source_repr.pretty_source(result.source))

dest_file = open(filename + '.h', 'w')
dest_file.write(prometeo.cgen.source_repr.pretty_source(result.header))
