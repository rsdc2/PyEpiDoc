from lxml.etree import _Element
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.epidoc.edition_elements.w import W
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.epidoc.representable import RepresentableElement


class Num(RepresentableElement):
    """
    Provides services for abbreviation expansions 
    given in <num> elements.
    """

    _w: W

    def __init__(self, e: _Element):
        super().__init__(e)

        if self._e.localname != 'name':
            raise TypeError('Element should be <name>.')
        self._w = W(e)

    @property
    def leiden_form(self) -> str:
        
        from .expan import Expan
        from .choice import Choice
        from .g import G

        element_classes: dict[str, type] = {
            'expan': Expan,
            'choice': Choice,
            'g': G
        }
        
        return leiden_str_from_children(self.e, element_classes, 'node')
    
    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .choice import Choice
        from .g import G

        element_classes: dict[str, type] = {
            'expan': Expan,
            'choice': Choice,
            'g': G
        }
        
        normalized_str = normalized_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )

        # Capitalize Roman numerals
        if self.charset == 'latin' and self.roman_numeral_chars_only:
            normalized_str = normalized_str.upper()
        
        # If part of abbreviation, spell out Roman numerals
        # TODO: add more numerals here
        if self._e.has_ancestor_by_name('abbr'):
            if normalized_str == 'II':
                return 'duo'

        return normalized_str
    
    @property
    def value(self) -> str:
        return self.get_attrib('value') or ''