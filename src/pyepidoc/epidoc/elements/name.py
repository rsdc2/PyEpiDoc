from __future__ import annotations
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
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Name):
            return False
        return self.leiden_str == other.leiden_str

    def __hash__(self):
        return hash(self.leiden_str)

    def __repr__(self) -> str:
        return f'Name("{self.leiden_str}")'

    @property
    def name_type(self) -> str:
        """
        Returns the @type property on the <name> element
        if it exists, or the empty string.
        """
        return self.get_attrib('type') or ""
    
    @property
    def nymref(self) -> str:
        """
        Returns the @nymRef property on the <name> element
        if it exists, or the empty string.
        """
        return self.get_attrib('nymRef') or ""