from functools import cached_property
from lxml.etree import _Element
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.epidoc.representable import Representable
from pyepidoc.shared.constants import XMLNS

class Space(Representable):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'space':
            raise TypeError('Element should be <space>.')
        
    def __repr__(self) -> str:
        return f'Space("{self.leiden_form}")'

    @property
    def leiden_form(self) -> str:
        return '(vac.)'
    
    @property
    def normalized_form(self) -> str:
        return '(vac.)'
    
    @property
    def quantity(self) -> str | None:
        return self.get_attrib('quantity')
    
    @cached_property
    def simple_lemmatized_edition_element(self) -> EpiDocElement:
        """
        Element for use in simple-lemmatized edition
        """
        return self.deepcopy()
    
    @property
    def unit(self) -> str | None:
        return self.get_attrib('unit')
    
    