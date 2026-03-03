from functools import cached_property
from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.epidoc.representable import RepresentableElement
from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_node_types import XmlElement


class Gap(RepresentableElement):
    """
    Provides services for abbreviation expansions 
    given in <gap> elements.
    """

    def __init__(self, e: TokenizableElement | TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'gap':
            raise TypeError(f'Element should be of type <gap>, '
                            f'but is of type <{self._e.localname}>.')
        
    def __repr__(self) -> str:
        return f'Gap("{self.leiden_form}")'
    
    @property
    def extent(self) -> str | None:
        return self.get_attr('extent')

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
    def simple_lemmatized_edition_element(self) -> RepresentableElement:
        """
        Element for use in simple-lemmatized edition
        """
        elem = self.deepcopy()
        elem._e.remove_children()
        elem._e.remove_attr('id', XMLNS)
        desc_elem = TokenizableElement.create('desc')
        desc_elem._e.text = self.simple_lemmatized_edition_form
        elem._e.append_node(desc_elem._e)
        return elem

    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        if self.get_attr('unit') == 'character' and self.get_attr('quantity') == '1':
            return "[.]"
        return "[-?-]"
    
    @property
    def unit(self) -> str | None:
        return self.get_attr('unit')
    
    