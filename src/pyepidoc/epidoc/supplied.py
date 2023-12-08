from lxml.etree import _Element
from .element import EpiDocElement
from .utils import (
    children_nodes_leiden_str
)

from .am import Am
from .ex import Ex
from .abbr import Abbr

element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex
}

class Supplied(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'supplied':
            raise TypeError('Element should be <supplied>.')

    def __str__(self) -> str:
        
        return ''.join([
            '[',
            children_nodes_leiden_str(self.e, element_classes),
            ']'
        ])