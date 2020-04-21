"""
Purpose:   Linear Algebra Parser
Based on:  SimpleCalc.py example (author Paul McGuire) in pyparsing-1.3.3
Author:    Mike Ellis
Copyright: Ellis & Grant, Inc. 2005
License:   You may freely use, modify, and distribute this software.
Warranty:  THIS SOFTWARE HAS NO WARRANTY WHATSOEVER. USE AT YOUR OWN RISK.
Notes: Parses infix linear algebra (LA) notation for vectors, matrices, and scalars.
       Output is C code function calls.  The parser can be run as an interactive
       interpreter or included as module to use for in-place substitution into C files
       containing LA equations.
       Supported operations are:
       OPERATION:              INPUT                    OUTPUT
       Scalar addition:        "a = b+c"                "a=(b+c)"
       Scalar subtraction:     "a = b-c"                "a=(b-c)"
       Scalar multiplication:  "a = b*c"                "a=b*c"
       Scalar division:        "a = b/c"                "a=b/c"
       Scalar exponentiation:  "a = b^c"                "a=pow(b,c)"
       Vector scaling:         "V3_a = V3_b * c"        "vCopy(a,vScale(b,c))"
       Vector addition:        "V3_a = V3_b + V3_c"     "vCopy(a,vAdd(b,c))"
       Vector subtraction:     "V3_a = V3_b - V3_c"     "vCopy(a,vSubtract(b,c))"
       Vector dot product:     "a = V3_b * V3_c"        "a=vDot(b,c)"
       Vector outer product:   "M3_a = V3_b @ V3_c"     "a=vOuterProduct(b,c)"
       Vector magn. squared:   "a = V3_b^Mag2"          "a=vMagnitude2(b)"
       Vector magnitude:       "a = V3_b^Mag"           "a=sqrt(vMagnitude2(b))"
       Matrix scaling:         "M3_a = M3_b * c"        "mCopy(a,mScale(b,c))"
       Matrix addition:        "M3_a = M3_b + M3_c"     "mCopy(a,mAdd(b,c))"
       Matrix subtraction:     "M3_a = M3_b - M3_c"     "mCopy(a,mSubtract(b,c))"
       Matrix multiplication:  "M3_a = M3_b * M3_c"     "mCopy(a,mMultiply(b,c))"
       Matrix by vector mult.: "V3_a = M3_b * V3_c"     "vCopy(a,mvMultiply(b,c))"
       Matrix inversion:       "M3_a = M3_b^-1"         "mCopy(a,mInverse(b))"
       Matrix transpose:       "M3_a = M3_b^T"          "mCopy(a,mTranspose(b))"
       Matrix determinant:     "a = M3_b^Det"           "a=mDeterminant(b)"
       The parser requires the expression to be an equation.  Each non-scalar variable
       must be prefixed with a type tag, 'M3_' for 3x3 matrices and 'V3_' for 3-vectors.
       For proper compilation of the C code, the variables need to be declared without
       the prefix as float[3] for vectors and float[3][3] for matrices. The operations do
       not modify any variables on the right-hand side of the equation.
       Equations may include nested expressions within parentheses. The allowed binary
       operators are '+-*/^' for scalars, and '+-*^@' for vectors and matrices with the
       meanings defined in the table above.
       Specifying an improper combination of operands, e.g. adding a vector to a matrix,
       is detected by the parser and results in a Python TypeError Exception. The usual cause
       of this is omitting one or more tag prefixes. The parser knows nothing about a
       a variable's C declaration and relies entirely on the type tags. Errors in C
       declarations are not caught until compile time.
Usage: To process LA equations embedded in source files, import this module and
       pass input and output file objects to the fprocess() function.  You can
       can also invoke the parser from the command line, e.g. 'python LAparser.py',
       to run a small test suite and enter an interactive loop where you can enter
       LA equations and see the resulting C code.
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

# Debugging flag can be set to either "debug_flag=True" or "debug_flag=False"
debug_flag = False

# ----------------------------------------------------------------------------
# Variables that hold intermediate parsing results and a couple of
# helper functions.
exprStack = []  # Holds operators and operands parsed from input.
# targetvar = None  # Holds variable name to left of '=' sign in LA equation.


def _pushFirst(str, loc, toks):
    if debug_flag:
        print("pushing ", toks[0], "str is ", str)
    exprStack.append(toks[0])


# def _assignVar(str, loc, toks):
#     global targetvar
#     targetvar = Operand(toks[0]


# -----------------------------------------------------------------------------
# The following statements define the grammar for the parser.

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
# solveop = Literal("~")
lpar = Literal("(").suppress()
rpar = Literal(")").suppress()
addop = plus | minus
multop = mult | div | outer | solveop
# expop = Literal("^")
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
# equation = (ident + assignop).setParseAction(_pushFirst) + expr + StringEnd()
equation = ident + assignop + expr + StringEnd()
# equation = (ident + assignop).setParseAction(_pushFirst) + expr + StringEnd()
# equation = expr + StringEnd()

# End of grammar definition
# -----------------------------------------------------------------------------
## The following are helper variables and functions used by the Binary Infix Operator
## Functions described below.

## We don't support unary negation for vectors and matrices
class UnaryUnsupportedError(Exception):
    pass

# def _isvec(ident, records):
#     if ident[0] == "-" and ident[1 : vplen + 1] == vprefix:
#         raise UnaryUnsupportedError
#     else:
#         return ident[0:vplen] == vprefix

class Operand:
    def __init__(self, oname, otype, osize, oexpr):
        self.name = oname
        self.type = otype
        self.size = osize
        self.expr = oexpr

# def _ismat(ident):
#     if ident[0] == "-" and ident[1 : mplen + 1] == mprefix:
#         raise UnaryUnsupportedError
#     else:
#         return ident[0:mplen] == mprefix

def _ismat(op):
    if op.type == 'pmat':
        return True
    else:
        return False

# def _isscalar(ident, records):
#     return not (_isvec(ident) or _ismat(ident))

## Binary infix operator (BIO) functions.  These are called when the stack evaluator
## pops a binary operator like '+' or '*".  The stack evaluator pops the two operand, a and b,
## and calls the function that is mapped to the operator with a and b as arguments.  Thus,
## 'x + y' yields a call to addfunc(x,y). Each of the BIO functions checks the prefixes of its
## arguments to determine whether the operand is scalar, vector, or matrix.  This information
## is used to generate appropriate C code.  For scalars, this is essentially the input string, e.g.
## 'a + b*5' as input yields 'a + b*5' as output.  For vectors and matrices, the input is translated to
## nested function calls, e.g. "V3_a + V3_b*5"  yields "V3_vAdd(a,vScale(b,5)".  Note that prefixes are
## stripped from operands and function names within the argument list to the outer function and
## the appropriate prefix is placed on the outer function for removal later as the stack evaluation
## recurses toward the final assignment statement.


def _addfunc(a, b, records):
    typed_record = records[0]
    # if _isvec(a) and _isvec(b):
    #     return "%svAdd(%s,%s)" % (vprefix, a[vplen:], b[vplen:])
    if _ismat(a) and _ismat(b):
        return Operand(a.name + '_+_' + b.name, 'pmat', [a.size[0], a.size[1]], \
            '_c_pmt_gead(1.0, %s, %s)' % (a.expr, b.expr))
    else:
        raise TypeError


def _subfunc(a, b, records):
    typed_record = records[0]
    # if _isscalar(a) and _isscalar(b):
    #     return "(%s-%s)" % (a, b)
    # if _isvec(a) and _isvec(b):
    #     return "%svSubtract(%s,%s)" % (vprefix, a[vplen:], b[vplen:])
    if _ismat(a) and _ismat(b):
        return Operand(a.name + '_-_' + b.name, 'pmat', [a.size[0], a.size[1]], \
            '_c_pmt_gead(-1.0, %s,%s)' % (a.expr, b.expr))
    else:
        raise TypeError


def _mulfunc(a, b, records):
    typed_record = records[0]
    if _ismat(a) and _ismat(b):
        return Operand(a.name + '_*_' + b.name, 'pmat', [a.size[0], b.size[1]], \
            '_c_pmt_gemm_nn(%s,%s)' % (a.expr, b.expr))
    else:
        raise TypeError


def _solvefunc(a, b, records):
    typed_record = records[0]
    if _ismat(a) and _ismat(b):
        return Operand(a.name + '_/_' + b.name, 'pmat', [a.size[0], b.size[1]], \
            '_c_pmt_getrsm(%s,%s)' % (a.expr, b.expr))
    else:
        raise TypeError

def _expfunc(a, b, records):
    typed_record = records[0]
    if _ismat(a) and b.name == "T":
        return Operand(a.name + '_T', 'pmat', [a.size[1], a.size[0]], \
            '_c_pmt_pmat_tran(%s)' % (a.expr))
    else:
        raise TypeError


def _assignfunc(a, b, records):
    typed_record = records[0]
    if _ismat(a) and _ismat(b):
        return Operand(a.name + '_+_' + b.name, 'pmat', [a.size[0], a.size[1]], \
            '_c_pmt_pmat_copy(%s,%s)' % (b.expr, a.expr))
    else:
        raise TypeError


## End of BIO func definitions
##----------------------------------------------------------------------------

# Map  operator symbols to corresponding BIO funcs
opn = {
    "+": (_addfunc),
    "-": (_subfunc),
    "*": (_mulfunc),
    ".": (_expfunc),
    "\\": (_solvefunc),
    "=": (_assignfunc),
}


def LAParser():
    def __init__(self):

##----------------------------------------------------------------------------
# Recursive function that evaluates the expression stack
def _evaluateStack(s, records):
    typed_record = records[0]
    var_dim_record = records[1]
    token = s.pop()
    print('s=', s)
    print('token=', token)
    if token == '.':
        token2 = s.pop()
        import pdb; pdb.set_trace()
        op2 = Operand(token2, [''], [0,0], '')
        op1 = _evaluateStack(s, records)
        result = opn[token](op1, op2, records)
        if debug_flag:
            print(result)
        return result
    elif token in ['+','-', '*', '/', '@', '\\', '=']:
        op2 = _evaluateStack(s, records)
        op1 = _evaluateStack(s, records)
        # print(op1, op2)
        result = opn[token](op1, op2, records)
        if debug_flag:
            print(result)
        return result
    else:
        return Operand(token, typed_record[token], var_dim_record[token], token) 


##----------------------------------------------------------------------------
# The parse function that invokes all of the above.
def parse(input_string, records):
    typed_record = records[0]
    var_dim_record = records[1]
    """
    Accepts an input string containing an LA equation, e.g.,
    "M3_mymatrix = M3_anothermatrix^-1" returns C code function
    calls that implement the expression.
    """

    global exprStack
    # global targetvar

    # Start with a blank exprStack and a blank targetvar
    exprStack = []
    targetvar = None

    if input_string != "":
        # try parsing the input string
        try:
            L = equation.parseString(input_string)
            targetvar = Operand(L[0], typed_record[L[0]], var_dim_record[L[0]], L[0]) 
        except ParseException as err:
            print("Parse Failure", file=sys.stderr)
            print(err.line, file=sys.stderr)
            print(" " * (err.column - 1) + "^", file=sys.stderr)
            print(err, file=sys.stderr)
            raise

        # show result of parsing the input string
        if debug_flag:
            print(input_string, "->", L)
            print("exprStack=", exprStack)

        # Evaluate the stack of parsed operands, emitting C code.
        try:
            result = _evaluateStack(exprStack, records)
        except TypeError:
            print(
                "Unsupported operation on right side of '%s'.\nCheck for missing or incorrect tags on non-scalar operands."
                % input_string,
                file=sys.stderr,
            )
            raise
        except UnaryUnsupportedError:
            print(
                "Unary negation is not supported for vectors and matrices: '%s'"
                % input_string,
                file=sys.stderr,
            )
            raise

        # Create final assignment and print it.
        if debug_flag:
            print("var=", targetvar)
        if targetvar != None:
            try:
                result = _assignfunc(targetvar, result, records)
            except TypeError:
                print(
                    "Left side tag does not match right side of '%s'" % input_string,
                    file=sys.stderr,
                )
                raise
            except UnaryUnsupportedError:
                print(
                    "Unary negation is not supported for vectors and matrices: '%s'"
                    % input_string,
                    file=sys.stderr,
                )
                raise

        else:
            print("Empty left side in '%s'" % input_string, file=sys.stderr)
            raise TypeError

        return result.expr


##-----------------------------------------------------------------------------------
def fprocess(expr, typed_record_json, var_dim_record_json, dim_record_json):
    """
   Scans an input file for LA equations between double square brackets,
   e.g. [[ M3_mymatrix = M3_anothermatrix^-1 ]], and replaces the expression
   with a comment containing the equation followed by nested function calls
   that implement the equation as C code. A trailing semi-colon is appended.
   The equation within [[ ]] should NOT end with a semicolon as that will raise
   a ParseException. However, it is ok to have a semicolon after the right brackets.
   Other text in the file is unaltered.
   The arguments are file objects (NOT file names) opened for reading and
   writing, respectively.
   """
    pattern = r"\[\[\s*(.*?)\s*\]\]"
    eqn = re.compile(pattern, re.DOTALL)

    with open(typed_record_json, 'r') as f:
        typed_record = json.load(f)

    with open(var_dim_record_json, 'r') as f:
        var_dim_record = json.load(f)

    with open(dim_record_json, 'r') as f:
        dim_record = json.load(f)

    records = dict()
    records[0] = typed_record
    records[1] = var_dim_record
    records[2] = dim_record

    def parser(mo):
        ccode = parse(mo.group(1), records)
        return "\n%s;\n" % (ccode)

    content = eqn.sub(parser, expr)
    return content
