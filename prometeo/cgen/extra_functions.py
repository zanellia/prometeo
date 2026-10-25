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
