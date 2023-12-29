from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children, normalized_str_from_children


class Num(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <num> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'num':
            raise TypeError('Element should be <num>.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        normalized_str = normalized_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )

        # Capitalize Roman numerals
        if self.charset == 'latin' and self.roman_numeral_chars_only:
            return normalized_str.upper()
        
        return normalized_str