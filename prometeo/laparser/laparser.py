"""
linear algebra parser adapted from laparser (Mike Ellis, Ellis & Grant, Inc 2005) 
"""

import re, sys
import json
from pyparsing import (
    Word,
    alphas,
    ParseException,
    Literal,
    CaselessLiteral,
    Combine,
    Optional,
    nums,
    Forward,
    ZeroOrMore,
    StringEnd,
    alphanums,
)

debug_flag = False

# variables that hold intermediate parsing results and a couple of
# helper functions.
exprStack = []  # Holds operators and operands parsed from input.

def _pushFirst(str, loc, toks):
    if debug_flag:
        print("pushing ", toks[0], "str is ", str)
    exprStack.append(toks[0])

# the following statements define the grammar for the parser.

point = Literal(".")
e = CaselessLiteral("E")
plusorminus = Literal("+") | Literal("-")
number = Word(nums)
integer = Combine(Optional(plusorminus) + number)
floatnumber = Combine(
    integer + Optional(point + Optional(number)) + Optional(e + integer)
)

lbracket = Literal("[")
rbracket = Literal("]")
ident = Forward()
## The definition below treats array accesses as identifiers. This means your expressions
## can include references to array elements, rows and columns, e.g., a = b[i] + 5.
## Expressions within []'s are not presently supported, so a = b[i+1] will raise
## a ParseException.
ident = Combine(
    Word(alphas + "-", alphanums + "_")
    + ZeroOrMore(lbracket + (Word(alphas + "-", alphanums + "_") | integer) + rbracket)
)

plus = Literal("+")
minus = Literal("-")
mult = Literal("*")
div = Literal("/")
solveop = Literal("\\")
outer = Literal("@")
lpar = Literal("(").suppress()
rpar = Literal(")").suppress()
addop = plus | minus
multop = mult | div | outer | solveop
expop = Literal(".")
assignop = Literal("=")

expr = Forward()
atom = (e | floatnumber | integer | ident).setParseAction(_pushFirst) | (
    lpar + expr.suppress() + rpar
)
factor = Forward()
factor << atom + ZeroOrMore((expop + factor).setParseAction(_pushFirst))

term = factor + ZeroOrMore((multop + factor).setParseAction(_pushFirst))
expr << term + ZeroOrMore((addop + term).setParseAction(_pushFirst))
equation = ident + assignop + expr + StringEnd()

# end of grammar definition
# -----------------------------------------------------------------------------
## the following are helper variables and functions used by the Binary Infix Operator
## Functions described below.

class Operand:
    def __init__(self, oname, otype, osize, oexpr):
        self.name = oname
        self.type = otype
        self.size = osize
        self.expr = oexpr

## end of BIO func definitions
##----------------------------------------------------------------------------

# map  operator symbols to corresponding BIO funcs
class LAParser():
    def __init__(self, typed_record_json, var_dim_record_json, dim_record_json):

        with open(typed_record_json, 'r') as f:
            typed_record = json.load(f)

        with open(var_dim_record_json, 'r') as f:
            var_dim_record = json.load(f)

        with open(dim_record_json, 'r') as f:
            dim_record = json.load(f)

        self.records = dict()
        self.records[0] = typed_record
        self.records[1] = var_dim_record
        self.records[2] = dim_record

        self.exprStack = []

        def _ismat(op):
            if op.type == 'pmat':
                return True
            else:
                return False

        def _addfunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and _ismat(b):
                return Operand(a.name + '_+_' + b.name, 'pmat', [a.size[0], a.size[1]], \
                    '_c_pmt_gead(1.0, %s, %s)' % (a.expr, b.expr))
            else:
                raise TypeError

        def _subfunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and _ismat(b):
                return Operand(a.name + '_-_' + b.name, 'pmat', [a.size[0], a.size[1]], \
                    '_c_pmt_gead(-1.0, %s,%s)' % (a.expr, b.expr))
            else:
                raise TypeError

        def _mulfunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and _ismat(b):
                return Operand(a.name + '_*_' + b.name, 'pmat', [a.size[0], b.size[1]], \
                    '_c_pmt_gemm_nn(%s,%s)' % (a.expr, b.expr))
            else:
                raise TypeError

        def _solvefunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and _ismat(b):
                return Operand(a.name + '_/_' + b.name, 'pmat', [a.size[0], b.size[1]], \
                    '_c_pmt_getrsm(%s,%s)' % (a.expr, b.expr))
            else:
                raise TypeError

        def _expfunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and b.name == "T":
                return Operand(a.name + '_T', 'pmat', [a.size[1], a.size[0]], \
                    '_c_pmt_pmat_tran(%s)' % (a.expr))
            else:
                raise TypeError

        def _assignfunc(a, b):
            typed_record = self.records[0]
            if _ismat(a) and _ismat(b):
                return Operand(a.name + '_+_' + b.name, 'pmat', [a.size[0], a.size[1]], \
                    '_c_pmt_pmat_copy(%s,%s)' % (b.expr, a.expr))
            else:
                raise TypeError

        self.opn = {
            "+": (_addfunc),
            "-": (_subfunc),
            "*": (_mulfunc),
            ".": (_expfunc),
            "\\": (_solvefunc),
            "=": (_assignfunc),
        }

    # recursive function that evaluates the expression stack
    def _evaluateStack(self, s):
        typed_record = self.records[0]
        var_dim_record = self.records[1]
        token = s.pop()
        if token == '.':
            token2 = s.pop()
            op2 = Operand(token2, [''], [0,0], '')
            op1 = self._evaluateStack(s)
            result = self.opn[token](op1, op2)
            if debug_flag:
                print(result)
            return result
        elif token in ['+','-', '*', '/', '@', '\\', '=']:
            op2 = self._evaluateStack(s)
            op1 = self._evaluateStack(s)
            result = self.opn[token](op1, op2)
            if debug_flag:
                print(result)
            return result
        else:
            return Operand(token, typed_record[token], var_dim_record[token], token) 


    # the parse function that invokes all of the above.
    def parse(self, expr):

        typed_record = self.records[0]
        var_dim_record = self.records[1]

        if expr != "":
            # try parsing the input string
            try:
                L = equation.parseString(expr)
                targetvar = Operand(L[0], typed_record[L[0]], var_dim_record[L[0]], L[0]) 
            except ParseException as err:
                print("Parse Failure", file=sys.stderr)
                print(err.line, file=sys.stderr)
                print(" " * (err.column - 1) + "^", file=sys.stderr)
                print(err, file=sys.stderr)
                raise

            # show result of parsing the input string
            if debug_flag:
                print(expr, "->", L)
                print("exprStack=", exprStack)

            # evaluate the stack of parsed operands, emitting C code.
            try:
                result = self._evaluateStack(exprStack)
            except TypeError:
                print(
                    "Unsupported operation on right side of '%s'.\nCheck for missing or incorrect tags on non-scalar operands."
                    % expr,
                    file=sys.stderr,
                )
                raise

            # create final assignment and print it.
            if debug_flag:
                print("var=", targetvar)
            if targetvar != None:
                try:
                    result = self.opn['='](targetvar, result)
                except TypeError:
                    print(
                        "Left side tag does not match right side of '%s'" % expr,
                        file=sys.stderr,
                    )
                    raise
            else:
                print("Empty left side in '%s'" % expr, file=sys.stderr)
                raise TypeError


            ccode = result.expr
            return "\n%s;\n" % (ccode)
