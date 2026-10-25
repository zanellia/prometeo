"""C code for the CasADi functions called by a transpiled program.

For each function f, CasADi generates c_pmt_cs_f, and a wrapper

    void c_pmt_casadi_f(struct pmat *in_0, ..., struct pmat *out_0, ...)

checks the matrix sizes, copies the inputs to static column-major buffers,
calls c_pmt_cs_f, and copies the results to the output matrices. All memory
is static: transpiled programs do not allocate memory at run time.
"""

import casadi as ca


def c_wrapper_name(name):
    return 'c_pmt_casadi_' + name


def c_prototype(name, f):
    args = ', '.join('struct pmat *{}'.format(a) for a in argument_names(f))
    return 'void {}({})'.format(c_wrapper_name(name), args)


def argument_names(f):
    return ['in_{}'.format(i) for i in range(f.n_in)] + ['out_{}'.format(i) for i in range(f.n_out)]


def generate(functions, directory):
    """Write casadi_functions.c/.h (CasADi) and casadi_wrappers.c to
    directory; return the names of the C sources."""
    cg = ca.CodeGenerator('casadi_functions.c', {'with_header': True})
    for name, f in functions.items():
        cg.add(f.renamed('c_pmt_cs_' + name))
    cg.generate(directory + '/')

    code = [
        '#include <stdio.h>',
        '#include <stdlib.h>',
        '#include "prometeo.h"',
        '#include "casadi_functions.h"',
        '',
        'static void c_pmt_casadi_check_size(struct pmat *A, int m, int n, const char *fun,',
        '        const char *arg) {',
        '    if (A->bmat->m != m || A->bmat->n != n) {',
        '        fprintf(stderr, "prometeo: CasADi function %s: %s has size %dx%d, expected %dx%d\\n",',
        '            fun, arg, A->bmat->m, A->bmat->n, m, n);',
        '        exit(1);',
        '    }',
        '}',
        '',
    ]
    for name, f in functions.items():
        cs = 'c_pmt_cs_' + name
        dense = f.renamed(cs)
        shapes = f.in_shapes + f.out_shapes
        args = argument_names(f)
        for a, (m, n) in zip(args, shapes):
            code.append('static casadi_real {}_{}[{}];'.format(cs, a, max(m * n, 1)))
        code += [
            'static const casadi_real *{}_arg[{}];'.format(cs, max(dense.sz_arg(), 1)),
            'static casadi_real *{}_res[{}];'.format(cs, max(dense.sz_res(), 1)),
            'static casadi_int {}_iw[{}];'.format(cs, max(dense.sz_iw(), 1)),
            'static casadi_real {}_w[{}];'.format(cs, max(dense.sz_w(), 1)),
            '',
            c_prototype(name, f) + ' {',
        ]
        for a, (m, n) in zip(args, shapes):
            code.append('    c_pmt_casadi_check_size({}, {}, {}, "{}", "{}");'.format(a, m, n, name, a))
        for i in range(f.n_in):
            a = 'in_{}'.format(i)
            m, n = f.in_shapes[i]
            code.append('    blasfeo_unpack_dmat({}, {}, {}->bmat, 0, 0, {}_{}, {});'.format(
                m, n, a, cs, a, m))
            code.append('    {}_arg[{}] = {}_{};'.format(cs, i, cs, a))
        for i in range(f.n_out):
            code.append('    {}_res[{}] = {}_out_{};'.format(cs, i, cs, i))
        code.append('    {}({}_arg, {}_res, {}_iw, {}_w, 0);'.format(cs, cs, cs, cs, cs))
        for i in range(f.n_out):
            a = 'out_{}'.format(i)
            m, n = f.out_shapes[i]
            code.append('    blasfeo_pack_dmat({}, {}, {}_{}, {}, {}->bmat, 0, 0);'.format(
                m, n, cs, a, m, a))
        code += ['}', '']
    with open(directory + '/casadi_wrappers.c', 'w') as out:
        out.write('\n'.join(code))
    return ['casadi_functions.c', 'casadi_wrappers.c']


def mangled_name(name, f):
    """Name of the call name(<pmat>, ..., <pmat>) in the code generator."""
    return '_Z{}{}'.format(len(name), name) + 'pmat' * (f.n_in + f.n_out)
