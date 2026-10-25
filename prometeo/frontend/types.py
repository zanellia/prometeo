"""Types of the prometeo language (see docs/source/language/language.rst)."""


class Type:
    """A prometeo type: a scalar, a matrix/vector, a List of elements or a
    user-defined class."""

    def __init__(self, name, elem=None):
        self.name = name
        self.elem = elem

    def __eq__(self, other):
        return isinstance(other, Type) and self.name == other.name and \
            self.elem == other.elem

    def __hash__(self):
        return hash((self.name, self.elem))

    def __str__(self):
        if self.elem is not None:
            return '{}[{}]'.format(self.name, self.elem)
        return self.name

    __repr__ = __str__


INT = Type('int')
FLOAT = Type('float')
# compile-time integer constant, usable as a matrix/vector dimension
DIMS = Type('dims')
# list of [rows, cols] pairs, used to size a List of matrices
DIMV = Type('dimv')
STR = Type('str')
NONE = Type('None')
PMAT = Type('pmat')
PVEC = Type('pvec')


def list_of(elem):
    return Type('List', elem)


def is_list(t):
    return t is not None and t.name == 'List'


def is_int_like(t):
    return t in (INT, DIMS)


def is_scalar(t):
    return t in (INT, FLOAT, DIMS)


# types that can be named in an annotation, besides user classes
ANNOTATION_TYPES = {
    'int': INT,
    'float': FLOAT,
    'pmat': PMAT,
    'pvec': PVEC,
    'List': None,  # element type given by the plist constructor
}

# element types of plist(<type>, <sizes>)
LIST_ELEMENT_TYPES = {'int': INT, 'float': FLOAT, 'pmat': PMAT, 'pvec': PVEC}
