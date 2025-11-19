from __future__ import annotations

from lxml.etree import _Element
from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.epidoc.representable import Representable
from pyepidoc.shared.iterables import maxone
from pyepidoc.shared.namespaces import XMLNS

class W(Representable):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self._e.localname != 'w':
            raise TypeError('Element should be <w>.')
        
    def __str__(self) -> str:
        return self.leiden_form
    
    def __repr__(self) -> str:
        return f'W("{self.leiden_form}")'

    @property
    def leiden_form(self) -> str:
        from .expan import Expan
        from .num import Num
        from .surplus import Surplus
        from .hi import Hi
        from .supplied import Supplied
        from .choice import Choice
        from .g import G
        from .lb import Lb

        element_classes: dict[str, type] = {
            'expan': Expan,
            'num': Num,
            'surplus': Surplus,
            'hi': Hi,
            'supplied': Supplied,
            'w': W,
            'choice': Choice,
            'g': G,
            'lb': Lb
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

    def move_xml_id_to_inner_w(self):
        """
        Move `@xml:id` attribute to inner `<w>` element 
        """
        xml_id = self.xml_id
        if self.xml_id is None:
            return
        
        inner_w = maxone(self.descendant_elements_by_local_name('w'), None, True)
        
        if inner_w is None:
            return
        
        inner_w.set_attrib('id', xml_id, XMLNS)
        self.remove_attr('id', XMLNS, True)

    @property
    def normalized_form(self) -> str:
        from .expan import Expan
        from .num import Num
        from .surplus import Surplus
        from .hi import Hi
        from .choice import Choice
        from .gap import Gap
        from .g import G

        element_classes: dict[str, type] = {
            'expan': Expan,
            'num': Num,
            'surplus': Surplus,
            'hi': Hi,
            'choice': Choice,
            'gap': Gap,
            'w': W,
            'g': G
        }
        
        return normalized_str_from_children(
            self.e, 
            element_classes, 
            'node'
        )
    
