from functools import cached_property
from lxml.etree import _Element
from pyepidoc.epidoc.representable import Representable
from ..utils import leiden_str_from_children


class Orig(Representable):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'orig':
            raise TypeError('Element should be <orig>.')

    def __repr__(self) -> str:
        return f'Orig("{self.leiden_form}")'

    @property
    def leiden_form(self) -> str:

        from .expan import Expan

        element_classes: dict[str, type] = {
            'expan': Expan
        }
        leiden_str = leiden_str_from_children(self.e, element_classes, 'node')
        
        if self.has_ancestor_by_name('choice'):
            return leiden_str
        
        return leiden_str.upper()
    
    @property
    def normalized_form(self) -> str:
        if self.has_ancestor_by_name('choice'):
            return ''
    
        return self.text_desc.upper()
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        if not self.has_parent('choice'):       
            return self.normalized_form
        return ""   