"""Built-in functions added to the code generator and the heap analysis from a
single table: mangled name -> (C function, argument types, return type)."""

extra_functions = {}

# math functions on floats
for name in ('sin', 'cos', 'tan', 'exp', 'log', 'sqrt'):
    extra_functions['_Z{}{}float'.format(len(name), name)] = (name, ['float'], 'float')

extra_functions.update({
    '_Z3absfloat': ('fabs', ['float'], 'float'),
    '_Z3absint': ('abs', ['int'], 'int'),
    '_Z3minfloatfloat': ('fmin', ['float', 'float'], 'float'),
    '_Z3maxfloatfloat': ('fmax', ['float', 'float'], 'float'),
    '_Z3minintint': ('c_pmt_imin', ['int', 'int'], 'int'),
    '_Z3maxintint': ('c_pmt_imax', ['int', 'int'], 'int'),
    # matrices and vectors with literal sizes, e.g. pmat(n, 1)
    '_Z4pmatdimsint': ('c_pmt_create_pmat', ['dims', 'int'], 'pmat'),
    '_Z4pmatintdims': ('c_pmt_create_pmat', ['int', 'dims'], 'pmat'),
    '_Z4pmatintint': ('c_pmt_create_pmat', ['int', 'int'], 'pmat'),
    '_Z4pvecint': ('c_pmt_create_pvec', ['int'], 'pvec'),
})

# matrix expressions (prometeo/frontend/matexpr.py) are lowered to these
for t in ('nn', 'nt', 'tn', 'tt'):
    name = 'pmt_gemm_ab_' + t
    extra_functions['_Z{}{}floatpmatpmatfloatpmatpmat'.format(len(name), name)] = \
        ('c_pmt_gemm_ab_' + t, ['float', 'pmat', 'pmat', 'float', 'pmat', 'pmat'], 'None')
extra_functions['_Z10pmat_scalefloatpmat'] = ('c_pmt_pmat_scale', ['float', 'pmat'], 'None')

# matrix expressions with blocks: a matrix argument is (M, row, col, rows, cols)
_view = ['pmat', 'int', 'int', 'int', 'int']
_view_functions = {
    'pmat_copy_view': ('c_pmt_pmat_copy_view', _view + _view),
    'pmat_tran_view': ('c_pmt_pmat_tran_view', _view + _view),
    'pmat_fill_view': ('c_pmt_pmat_fill_view', ['float'] + _view),
    'pmat_scale_view': ('c_pmt_pmat_scale_view', ['float'] + _view),
    'pmt_gead_view': ('c_pmt_gead_view', ['float'] + _view + _view),
}
for t in ('nn', 'nt', 'tn', 'tt'):
    _view_functions['pmt_gemm_view_' + t] = ('c_pmt_gemm_view_' + t,
        ['float'] + _view + _view + ['float'] + _view + _view)
for name, (c_name, arg_types) in _view_functions.items():
    extra_functions['_Z{}{}{}'.format(len(name), name, ''.join(arg_types))] = (c_name, arg_types, 'None')

# vector expressions: a vector argument is (v, first element, size)
_vview = ['pvec', 'int', 'int']
_vector_functions = {
    'pvec_copy_view': ('c_pmt_pvec_copy_view', _vview + _vview, 'None'),
    'pvec_fill_view': ('c_pmt_pvec_fill_view', ['float'] + _vview, 'None'),
    'pvec_scale_view': ('c_pmt_pvec_scale_view', ['float'] + _vview, 'None'),
    'pvec_axpy_view': ('c_pmt_pvec_axpy_view', ['float'] + _vview + _vview, 'None'),
    'pvec_dot_view': ('c_pmt_pvec_dot_view', _vview + _vview, 'float'),
    'pmt_potrsv_view': ('c_pmt_potrsv_view', ['pmat'] + _vview, 'None'),
}
for t in ('n', 't'):
    _vector_functions['pmt_gemv_view_' + t] = ('c_pmt_gemv_view_' + t,
        ['float'] + _view + _vview + ['float'] + _vview + _vview, 'None')
for name, (c_name, arg_types, ret_type) in _vector_functions.items():
    extra_functions['_Z{}{}{}'.format(len(name), name, ''.join(arg_types))] = (c_name, arg_types, ret_type)
