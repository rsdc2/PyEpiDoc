from lxml.etree import _Element
from ..epidoc_element import EpiDocElement
from ..utils import leiden_str_from_children, normalized_str_from_children

from .orig import Orig
from .reg import Reg
from .sic import Sic
from .corr import Corr


class Choice(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <choice> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'choice':
            raise TypeError('Element should be <choice>.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan,
            'orig': Orig,
            'reg': Reg,
            'sic': Sic,
            'corr': Corr
        }
    
        return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan,
            'orig': Orig,
            'reg': Reg,
            'sic': Sic,
            'corr': Corr
        }        

        return normalized_str_from_children(self.e, element_classes, 'node')
