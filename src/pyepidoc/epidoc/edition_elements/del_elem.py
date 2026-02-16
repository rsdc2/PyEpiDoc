from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from .expan import Expan

element_classes: dict[str, type] = {
    'expan': Expan
}


class Del(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """
    def __init__(self, e: XmlElement | TeiElement):

        super().__init__(e)

        if self._e.localname != 'del':
            raise TypeError(f'Element should be <del> not {self._e.localname}.')

    @property
    def leiden_form(self) -> str:
        
        return ''.join([
            '⟦',
            leiden_str_from_children(self._e, element_classes, 'node'),
            '⟧'
        ])
    
    @property
    def normalized_form(self) -> str:
        return normalized_str_from_children(self._e, element_classes, 'node')