from __future__ import annotations
from lxml.etree import _Element

from pyepidoc.epidoc.representable import RepresentableElement
from .w import W

class Name(RepresentableElement):
    """
    Provides services for string representation of <w> elements.
    """

    _w: W

    def __init__(self, e: _Element):
        super().__init__(e)

        if self._e.localname != 'name':
            raise TypeError('Element should be <name>.')
        self._w = W(e)
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Name):
            return False
        return self._w.leiden_str == other._w.leiden_str

    def __hash__(self):
        return hash(self.leiden_str)

    def __repr__(self) -> str:
        return f'Name("{self._w.leiden_str}")'

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