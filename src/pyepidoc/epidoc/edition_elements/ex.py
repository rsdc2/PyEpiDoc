from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement


class Ex(TokenizableElement):
    """
    Provides services for abbreviation expansions 
    given in <ex> elements.
    """

    def __init__(self, e: TokenizableElement | TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'ex':
            raise TypeError(f'Element should be of type <ex>, '
                            f'but is of type <{self._e.localname}>.')

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