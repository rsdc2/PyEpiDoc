from lxml.etree import _Element
from ..element import EpiDocElement
from pyepidoc.epidoc.utils import localname


class Ex(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if localname(e) != 'ex':
            raise TypeError(f'Element should be of type <ex>, '
                            f'but is of type <{localname(e)}>.')


    def __str__(self) -> str:
        return ''.join([
            '(',
            self.text_desc_compressed_whitespace,
            ')'
        ])

    @property
    def normalized_form(self) -> str:
        return self.text_desc_compressed_whitespace