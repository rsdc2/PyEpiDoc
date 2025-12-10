from lxml.etree import _Element
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement

from .abbr import Abbr
from .am import Am
from .ex import Ex

element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex
}


class Unclear(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <unclear> elements.
    """

    def __init__(self, e: _Element | TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'unclear':
            raise TypeError(f'Element should be <unclear> not {self._e.localname}.')


    @property
    def leiden_form(self) -> str:
        
        return ''.join([
            ''.join(map(
                lambda char: char + '\u0323', 
                leiden_str_from_children(self._e._e, element_classes, 'node'))
            )
        ])

    @property
    def normalized_form(self) -> str:
        return normalized_str_from_children(self._e._e, element_classes, 'node')