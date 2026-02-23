from functools import cached_property

from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.representable import RepresentableElement
from pyepidoc.epidoc.utils import leiden_str_from_children


class Orig(RepresentableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'orig':
            raise TypeError(f'Element should be <orig> not {self._e.localname}.')

    def __repr__(self) -> str:
        return f'Orig("{self.leiden_form}")'

    @property
    def leiden_form(self) -> str:

        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        leiden_str = leiden_str_from_children(self._e, element_classes)
        
        if self._e.has_ancestor_by_name('choice'):
            return leiden_str
        
        return leiden_str.upper()
    
    @property
    def normalized_form(self) -> str:
        if self._e.has_ancestor_by_name('choice'):
            return ''
    
        return self._e.text_desc.upper()
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        if not self._e.has_parent('choice'):       
            return self.normalized_form
        return ''