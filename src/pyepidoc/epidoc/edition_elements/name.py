from __future__ import annotations
from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from .w import _W


class Name(_W):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'name':
            raise TypeError(f'Element should be <w> not {self._e.localname}.')
        
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
        return self.get_attr('type') or ""
    
    @property
    def nymref(self) -> str:
        """
        Returns the @nymRef property on the <name> element
        if it exists, or the empty string.
        """
        return self.get_attr('nymRef') or ""