from __future__ import annotations
from typing import Optional

from lxml.etree import _Element 

from ..element import EpiDocElement

from ...xml import XmlElement
from ...shared.constants import XMLNS

from .ab import Ab


class Lg(Ab):

    """
    <lg> = line group (for poetic texts)
    """

    def __init__(self, e:Optional[_Element | EpiDocElement | XmlElement]=None):

        if type(e) not in [_Element, EpiDocElement, XmlElement] and e is not None:
            raise TypeError('e should be _Element or Element type, or None.')

        if type(e) is _Element:
            self._e = e
        elif type(e) is EpiDocElement:
            self._e = e.e
        elif type(e) is XmlElement:
            self._e = e.e

        if self.tag.name != 'lg':
            raise TypeError('Element should be of type <lg>.')

