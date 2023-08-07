from typing import Optional
from lxml.etree import _Element
from ..base import Element


class Ex(Element):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e:Optional[_Element]=None):
        if type(e) is not _Element and e is not None:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if self.tag.name != 'ex':
            raise TypeError('Element should be of type <ex>.')

    def __str__(self) -> str:
        return ''.join([
            '(',
            self.text_desc_compressed_whitespace,
            ')'
        ])