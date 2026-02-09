from lxml.etree import _Element
from ..tokenizable_element import TokenizableElement
from pyepidoc.shared.enums import AtomicTokenType
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement

class G(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element | TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'g':
            raise TypeError(f'Element should be <g> not {self._e.localname}.')
        
    def __str__(self) -> str:
        return self.leiden_form

    @property
    def ref(self) -> str:
        return self.get_attr('ref') or ''    

    @property
    def leiden_form(self) -> str:
        if self._e.has_ancestors_by_names(AtomicTokenType.values()):
            return self._e.text_desc_compressed_whitespace
        
        return ' ' + self._e.text_desc_compressed_whitespace + ' '

    @property
    def normalized_form(self) -> str:
        if self._e.text_desc_compressed_whitespace == '☧':
            return 'Χρ'
        
        return ''