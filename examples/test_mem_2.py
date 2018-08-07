from prometeo.mem.ast_analyzer import get_call_graph
import ast
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Input .py file', required=True)
    args = parser.parse_args()
    tree = ast.parse(open(args.input).read())
    call_graph = get_call_graph(tree)
