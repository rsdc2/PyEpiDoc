from __future__ import annotations

from lxml.etree import _Element
from ..element import EpiDocElement
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children


class W(EpiDocElement):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'w':
            raise TypeError('Element should be <w>.')
        
    def __str__(self) -> str:
        return self.leiden_form

    @property
    def leiden_form(self) -> str:
        from .expan import Expan
        from .num import Num
        from .surplus import Surplus
        from .hi import Hi

        element_classes: dict[str, type] = {
            'expan': Expan,
            'num': Num,
            'surplus': Surplus,
            'hi': Hi
        }
        
        return leiden_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )
    
    @property
    def leiden_str(self) -> str:
        return self.leiden_form

    @property
    def lemma(self) -> str | None:
        """
        Return the lemma of the <w> element.
        """
        return self.get_attrib('lemma')
    
    @lemma.setter
    def lemma(self, value: str) -> None:
        
        """
        Set the @lemma attribute on the <w> element.
        """

        if not isinstance(value, str):
            raise TypeError(f'Cannot set attribute on {self} because lemma value is not a string.')
        
        self.lemma = value

    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .num import Num
        from .surplus import Surplus
        from .hi import Hi
        from .choice import Choice

        element_classes: dict[str, type] = {
            'expan': Expan,
            'num': Num,
            'surplus': Surplus,
            'hi': Hi,
            'choice': Choice
        }
        
        return normalized_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )
    
