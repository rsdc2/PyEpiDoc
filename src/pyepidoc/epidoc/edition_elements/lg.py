from __future__ import annotations

from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.xml import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.epidoc.token_container import TokenContainer


class Lg(TokenContainer):

    """
    <lg> = line group (for poetic texts)
    """

    def __init__(self, e: TeiElement | XmlElement):

        if type(e) not in [TeiElement, XmlElement]:
            raise TypeError('e should be of type TokenizableElement or XmlElement.')

        if type(e) is TokenizableElement:
            self._e = e.e
        elif type(e) is XmlElement:
            self._e = e.e

        if self._e.tag.name != 'lg':
            raise TypeError('Element should be of type <lg>.')

