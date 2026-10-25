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
    tree = expand_dimv(tree)
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


def eval_dims(node, dims):
    """Value of an integer expression of literals and dims constants, or None."""
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.Name):
        return dims.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        left, right = eval_dims(node.left, dims), eval_dims(node.right, dims)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        return left * right
    return None


def expand_dimv(tree):
    """Rewrite sizes : dimv = [[m, n]] * k as an explicit list of k pairs."""
    dims = {}
    for stmt in tree.body:
        if not (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
                and isinstance(stmt.annotation, ast.Name) and stmt.value is not None):
            continue
        if stmt.annotation.id == 'dims':
            value = eval_dims(stmt.value, dims)
            if value is not None:
                dims[stmt.target.id] = value
        elif stmt.annotation.id == 'dimv' and isinstance(stmt.value, ast.BinOp) \
                and isinstance(stmt.value.op, ast.Mult) and isinstance(stmt.value.left, ast.List):
            count = eval_dims(stmt.value.right, dims)
            if count is not None and count > 0:
                elts = [deepcopy(e) for _ in range(count) for e in stmt.value.left.elts]
                stmt.value = ast.copy_location(ast.List(elts=elts, ctx=ast.Load()), stmt.value)
    return tree
