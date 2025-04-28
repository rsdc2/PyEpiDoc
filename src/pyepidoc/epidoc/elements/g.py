from lxml.etree import _Element
from ..element import EpiDocElement
from pyepidoc.epidoc.enums import AtomicTokenType

class G(EpiDocElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'g':
            raise TypeError('Element should be <g>.')

    def __str__(self) -> str:
        return self.leiden_form

    @property
    def ref(self) -> str:
        return self.get_attrib('ref') or ''    

    @property
    def leiden_form(self) -> str:
        if self.has_ancestors_by_names(AtomicTokenType.values()):
            return self.text_desc_compressed_whitespace
        
        return ' ' + self.text_desc_compressed_whitespace + ' '

    @property
    def normalized_form(self) -> str:
        if self.text_desc_compressed_whitespace == '☧':
            return 'Χρ'
        
        return ''