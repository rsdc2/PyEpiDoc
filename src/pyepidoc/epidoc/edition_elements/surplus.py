from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement

from .abbr import Abbr
from .am import Am
from .ex import Ex

element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex
}


class Surplus(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'surplus':
            raise TypeError('Element should be <surplus>.')

    @property
    def leiden_form(self) -> str:
        
        return ''.join([
            '{',
            leiden_str_from_children(self._e, element_classes),
            '}'
        ])

    @property
    def normalized_form(self) -> str:
        return ''