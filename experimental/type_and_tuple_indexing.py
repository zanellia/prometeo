class _psize:
    _inner_get = False

    def __getitem__(self, index):
        if self._inner_get is True:
            self._inner_get = False
            return self[index]

        self._inner_get = True
        return self

psize = _psize()

a : psize[0] = 1
a : psize[0][1] = 1

from typing import Any
class _psize2:

    def __getitem__(self, index):
        if isinstance(index, tuple):
            if len(index) == 2:
                return Any
        else:
            raise Exception ('pmat dimensions should be a 2-dimensional tuple.')

psize2 = _psize2()
a : psize2[0,1] = 1

