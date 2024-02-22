from lxml.etree import _Element
from .w import W


class Name(W):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'name':
            raise TypeError('Element should be <name>.')

    @property
    def name_type(self) -> str:
        return self.get_attrib('type') or ""