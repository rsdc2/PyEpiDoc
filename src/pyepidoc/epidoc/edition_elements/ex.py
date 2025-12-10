from lxml.etree import _Element
from pyepidoc.epidoc.edition_element import EditionElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.epidoc.utils import localname


class Ex(EditionElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: _Element | EditionElement | TeiElement | XmlElement):

        super().__init__(e)

        if localname(self._e._e) != 'ex':
            raise TypeError(f'Element should be of type <ex>, '
                            f'but is of type <{localname(self._e._e)}>.')

    @property
    def leiden_form(self) -> str:
        return ''.join([
            '(',
            self._e.text_desc_compressed_whitespace,
            ')'
        ])

    @property
    def normalized_form(self) -> str:
        return self._e.text_desc_compressed_whitespace