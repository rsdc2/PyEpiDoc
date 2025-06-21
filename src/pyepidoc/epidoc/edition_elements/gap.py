from functools import cached_property
from lxml.etree import _Element
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.epidoc.representable import Representable
from pyepidoc.shared.constants import XMLNS

class Gap(Representable):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'gap':
            raise TypeError('Element should be <gap>.')
        
    def __repr__(self) -> str:
        return f'Gap("{self.leiden_form}")'
    
    @property
    def extent(self) -> str | None:
        return self.get_attrib('extent')

    @property
    def leiden_form(self) -> str:
        if self.unit is None or self.extent is None:
            return ' [-?-] '
        
        if self.unit == 'character' and self.extent == 'unknown':
            return ' [-?-] '
        
        return f' [-{self.extent}-] '
    
    @property
    def normalized_form(self) -> str:
        if self.unit is None or self.extent is None:
            return '[-?-]'
        
        if self.unit == 'character' and self.extent == 'unknown':
            return '[-?-]'
        
        return f' [-{self.extent}-] '
    
    @cached_property
    def simple_lemmatized_edition_element(self) -> EpiDocElement:
        """
        Element for use in simple-lemmatized edition
        """
        elem = self.deepcopy()
        elem.remove_children()
        elem.remove_attr('id', XMLNS)
        desc_elem = EpiDocElement.create_new('desc')
        desc_elem.text = self.simple_lemmatized_edition_form
        elem.append_node(desc_elem.e)
        return elem

    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        return "[-?-]"
    
    @property
    def unit(self) -> str | None:
        return self.get_attrib('unit')
    
    