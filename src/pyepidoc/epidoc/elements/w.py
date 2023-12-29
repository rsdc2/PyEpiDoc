from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children, normalized_str_from_children


class W(EpiDocElement):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'w':
            raise TypeError('Element should be <w>.')

    # def __str__(self) -> str:
        
    #     from .expan import Expan

    #     element_classes: dict[str, type] = {
    #         'expan': Expan
    #     }
        
    #     return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .num import Num

        element_classes: dict[str, type] = {
            'expan': Expan,
            'num': Num
        }
        
        return normalized_str_from_children(self.e, element_classes, 'node')