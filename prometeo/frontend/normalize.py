"""Rewrite equivalent forms of prometeo code into the ones handled by the
checker and the code generator."""

import ast
from copy import deepcopy


class AugAssignToAssign(ast.NodeTransformer):
    """Rewrite x += e as x = x + e (also for elements, A[i, j] += e)."""

    def visit_AugAssign(self, node):
        target = deepcopy(node.target)
        value = deepcopy(node.target)
        for n in ast.walk(value):
            if hasattr(n, 'ctx'):
                n.ctx = ast.Load()
        value = ast.copy_location(ast.BinOp(left=value, op=node.op, right=node.value), node)
        return ast.copy_location(ast.Assign(targets=[target], value=value), node)


def normalize(tree):
    """Rewrite equivalent forms into the ones handled by the checker and the
    code generator."""
    tree = normalize_plist_types(tree)
    tree = AugAssignToAssign().visit(tree)
    return ast.fix_missing_locations(tree)


def normalize_plist_types(tree):
    """Rewrite plist(pmat, ...) as plist('pmat', ...): the code generator and
    the heap analysis expect the element type of a plist as a string."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == 'plist' and node.args \
                and isinstance(node.args[0], ast.Name):
            node.args[0] = ast.copy_location(ast.Constant(node.args[0].id), node.args[0])
    return tree
