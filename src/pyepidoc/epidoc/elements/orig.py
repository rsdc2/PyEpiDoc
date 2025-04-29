from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children


class Orig(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'orig':
            raise TypeError('Element should be <orig>.')

    @property
    def leiden_form(self) -> str:

        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        leiden_str = leiden_str_from_children(self.e, element_classes, 'node')
        
        if self.has_ancestor_by_name('choice'):
            return leiden_str
        
        return leiden_str.upper()
    
    @property
    def normalized_form(self) -> str:
        # breakpoint()
        if self.has_ancestor_by_name('choice'):
            return ''
    
        return self.text_desc.upper()