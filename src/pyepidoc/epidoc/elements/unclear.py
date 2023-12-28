from lxml.etree import _Element
from ..element import EpiDocElement
from ..utils import leiden_str_from_children, normalized_str_from_children

from .abbr import Abbr
from .am import Am
from .ex import Ex

element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex
}


class Unclear(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <unclear> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.local_name != 'unclear':
            raise TypeError('Element should be <unclear>.')

    def __str__(self) -> str:
        
        return ''.join([
            ''.join(map(
                lambda char: char + '\u0323', 
                leiden_str_from_children(self.e, element_classes, 'node'))
            )
        ])

    @property
    def normalized_form(self) -> str:
        return normalized_str_from_children(self.e, element_classes, 'node')