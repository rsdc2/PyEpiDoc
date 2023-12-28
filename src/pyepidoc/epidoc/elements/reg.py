from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children


class Reg(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'reg':
            raise TypeError('Element should be <reg>.')

    def __str__(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        return self.text_desc_compressed_whitespace
