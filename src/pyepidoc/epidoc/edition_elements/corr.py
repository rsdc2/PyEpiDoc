from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.utils import leiden_str_from_children
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement


class Corr(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'corr':
            raise TypeError(f'Element should be <corr> not {self._e.localname}.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        return leiden_str_from_children(self._e, element_classes)
    
    @property
    def normalized_form(self) -> str:
        return self._e.text_desc_compressed_whitespace
