from lxml.etree import _Element
from .element import EpiDocElement


class Ex(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.tag.name != 'ex':
            raise TypeError('Element should be of type <ex>.')

    def __str__(self) -> str:
        return ''.join([
            '(',
            self.text_desc_compressed_whitespace,
            ')'
        ])