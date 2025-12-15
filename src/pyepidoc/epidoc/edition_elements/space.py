from functools import cached_property
from lxml.etree import _Element
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.representable import RepresentableElement
from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement

class Space(RepresentableElement):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: _Element | TeiElement | XmlElement):
        super().__init__(e)

        if self._e.localname != 'space':
            raise TypeError(f'Element should be <space> but is <{self.e.localname}>.')
        
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
    def simple_lemmatized_edition_element(self) -> EditionElement:
        """
        Element for use in simple-lemmatized edition
        """
        return self.deepcopy()
    
    @property
    def unit(self) -> str | None:
        return self.get_attrib('unit')
    
    