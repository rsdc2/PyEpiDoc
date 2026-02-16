from __future__ import annotations
from typing import Optional

from ..tokenizable_element import TokenizableElement
from ...xml import XmlElement
from .ab import Ab


class L(Ab):

    """
    <l> = line (for poetic(?) texts)
    """

    def __init__(self, e: TokenizableElement | XmlElement):

        if type(e) not in [TokenizableElement, XmlElement]:
            raise TypeError('e should be _Element or Element type.')

        if type(e) is TokenizableElement:
            self._e = e.e
        elif type(e) is XmlElement:
            self._e = e.e

        if self._e.tag.name != 'l':
            raise TypeError('Element should be of type <l>.')

