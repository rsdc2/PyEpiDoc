from lxml.etree import _Element
from .element import EpiDocElement
from .utils import leiden_str_from_children

from .expan import Expan

element_classes: dict[str, type] = {
    'expan': Expan
}


class Del(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'del':
            raise TypeError('Element should be <supplied>.')

    def __str__(self) -> str:
        
        return ''.join([
            '⟦',
            leiden_str_from_children(self.e, element_classes, 'node'),
            '⟧'
        ])