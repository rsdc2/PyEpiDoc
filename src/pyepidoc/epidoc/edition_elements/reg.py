from lxml.etree import _Element
from ..edition_element import EditionElement
from ..utils import leiden_str_from_children


class Reg(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self._e.localname != 'reg':
            raise TypeError('Element should be <reg>.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        if self._e.has_ancestor_by_name('choice'):
            return ''

        return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        return self._e.text_desc_compressed_whitespace
