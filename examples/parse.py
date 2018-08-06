import prometeo
import ast
import astpretty
import typing
# import code_gen
# import code_gen_c
# from source_repr import pretty_source

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


filename = 'code.prmt'
# filename = 'test_prmt_mat_compact.prmt'
# filename = 'test_prmt_mat.prmt'
module_name = 'code'
tree = ast.parse(''.join(open(filename)))
astpretty.pprint(tree)

result  = prometeo.cgen.code_gen_c.to_source(tree, module_name)

print("source = \n", prometeo.cgen.source_repr.pretty_source(result.source))
print("header = \n", prometeo.cgen.source_repr.pretty_source(result.header))

dest_file = open('code.c', 'w')
dest_file.write(prometeo.cgen.source_repr.pretty_source(result.source))

dest_file = open('code.h', 'w')
dest_file.write(prometeo.cgen.source_repr.pretty_source(result.header))
