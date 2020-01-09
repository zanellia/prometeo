# from prometeo.mem.ast_analyzer import get_call_graph
from prometeo.mem.ast_analyzer import compute_reach_graph
from prometeo.mem.ast_analyzer_2 import ast_visitor
from prometeo.mem.ast_analyzer_2 import compute_reach_graph
# from prometeo.cgen.code_gen import to_source
import ast
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input .py file', required=True)
    args = parser.parse_args()
    tree = ast.parse(open(args.input).read())
    # call_graph = get_call_graph(tree)

    visitor = ast_visitor()
    # import pdb; pdb.set_trace()
    visitor.visit(tree) 
    call_graph = visitor.callees
    print(call_graph)

    # to_source(tree)
    # print('call graph:\n', call_graph)
    # import pdb; pdb.set_trace()
    reach_map = compute_reach_graph(call_graph)
    print('reach_map:\n', reach_map)
