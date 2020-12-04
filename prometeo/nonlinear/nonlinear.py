import casadi as ca
from numpy import *
from tokenize import tokenize, untokenize, NUMBER, STRING, NAME, OP
from io import BytesIO
from ..linalg import pmat, pvec
import inspect
import os
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

def pmat_to_numpy(A):
    np_A = ones((A.m, A.n))
    for i in range(A.m):
        for j in range(A.n):
            np_A[i,j] = A[i,j]
    return np_A

def pvec_to_numpy(v):
    np_v = ones((v.m, 1))
    for i in range(v.m):
        np_v[i] = v[i]
    return np_v

class pfun:

    def __init__(self, fun_name, expr, variables):
        # get stack
        stack =  inspect.stack()

        prefix = 'global'
        for i in range(len(stack)-5, 0, -1):
            prefix = prefix + '_' + stack[i].function
        # tokenize
        # tokens = tokenize(BytesIO(expr.encode('utf-8')).readline)
        # for token in tokens:
        #     print(token)

        tokens = tokenize(BytesIO(expr.encode('utf-8')).readline)

        # convert variables to Numpy
        np_var_names = []
        ca_var_names = []
        ca_fun_args = ''
        # ca_variables = []
        fun_descriptor = dict()
        fun_descriptor['args'] = []
        for var_name, var in variables.items():
            if isinstance(var, pmat):
                dec_code = 'np_' + var_name + '= pmat_to_numpy(var)'
                exec(dec_code)
                np_var_names.append(var_name)
            elif isinstance(var, pvec):
                np_var_names.append(var_name)
                dec_code = 'np_' + var_name + '= pvec_to_numpy(var)'
                exec(dec_code)
            elif isinstance(var, ca.SX) or isinstance(var, ca.MX):
                dec_code = 'ca_' + var_name + '= ca.SX.sym(\'ca_' + var_name + \
                    '\',' + str(var.shape[0]) + ',' + str(var.shape[1]) + ')'
                exec(dec_code)
                ca_var_names.append(var_name)
                ca_fun_args = ca_fun_args + ', ca_' + var_name 
                fun_descriptor['args'].append({'name' : var_name, 'size' : (var.shape[0],var.shape[1])})
            else:
                raise Exception('Variable {} of unknown type {}'.format(var, type(var)))

        # strip leading comma from ca_fun_args
        ca_fun_args = ca_fun_args.replace(', ', '', 1)

        result = []
        # find variables in expr
        for toknum, tokval, _, _, _ in tokens:
            if toknum == NAME and tokval in np_var_names:  # replace NUMBER tokens
                result.append((toknum, 'np_' + tokval))
            elif toknum == NAME and tokval in ca_var_names:  # replace NUMBER tokens
                result.append((toknum, 'ca_' + tokval))
            else:
                result.append((toknum, tokval))

        ca_expr = untokenize(result).decode('utf-8').replace(" ", "")
        scoped_fun_name = prefix + '_' + fun_name
        fun_descriptor['name'] = scoped_fun_name 
        dec_code = 'fun = ca.Function(\'' + scoped_fun_name+ '\', [' \
            + ca_fun_args + '], [' + ca_expr + '])'

        exec(dec_code)
        
        # get CasADi function from locals()
        self._ca_fun = locals()['fun']

        # generate C code
        if not os.path.exists('__pmt_cache__'):
            os.makedirs('__pmt_cache__')
        os.chdir('__pmt_cache__')

        self._ca_fun.generate(scoped_fun_name + '.c')
        import pdb; pdb.set_trace()

        # render templated wrapper
        env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
        tmpl = env.get_template("casadi_wrapper.c.in")
        code = tmpl.render(fun_descriptor = fun_descriptor)
        with open('casadi_wrapper_' + scoped_fun_name + '.c', "w+") as f:
            f.write(code)

        tmpl = env.get_template("casadi_wrapper.h.in")
        code = tmpl.render(fun_descriptor = fun_descriptor)
        with open('casadi_wrapper_' + scoped_fun_name + '.h', "w+") as f:
            f.write(code)

        os.chdir('..')

    def __call__(self, args):
        return self._ca_fun(args).full()
