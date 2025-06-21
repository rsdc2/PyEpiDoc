from lxml.etree import _Element

from .w import W

class Measure(W):

    def __init__(self, e: _Element):
        if not isinstance(e, _Element):
            raise TypeError('e should be an instance of type _Element.')

        self._e = e

        if self.localname != 'measure':
            raise TypeError('Element should be <measure>.')