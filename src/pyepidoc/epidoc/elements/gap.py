from lxml.etree import _Element
from pyepidoc.epidoc.representable import Representable


class Gap(Representable):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'gap':
            raise TypeError('Element should be <gap>.')

    @property
    def extent(self) -> str | None:
        return self.get_attrib('extent')

    @property
    def leiden_form(self) -> str:
        if self.unit is None or self.extent is None:
            return ' [-?-] '
        
        if self.unit == 'character' and self.extent == 'unknown':
            return ' [-?-] '
        
        return f' [-{self.extent}-] '
    
    @property
    def normalized_form(self) -> str:
        if self.unit is None or self.extent is None:
            return '[-?-]'
        
        if self.unit == 'character' and self.extent == 'unknown':
            return '[-?-]'
        
        return f' [-{self.extent}-] '
    
    @property
    def unit(self) -> str | None:
        return self.get_attrib('unit')