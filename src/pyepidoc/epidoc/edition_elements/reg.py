from lxml.etree import _Element
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.utils import leiden_str_from_children


class Reg(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element | XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'reg':
            raise TypeError(f'Element should be <reg> not {self._e.localname}.')

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        
        if self._e.has_ancestor_by_name('choice'):
            return ''

        return leiden_str_from_children(self._e._e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        return self._e.text_desc_compressed_whitespace
