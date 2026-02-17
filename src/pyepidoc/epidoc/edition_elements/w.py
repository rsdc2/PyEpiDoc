from __future__ import annotations

from pyepidoc.epidoc.utils import leiden_str_from_children, normalized_str_from_children
from pyepidoc.epidoc.representable import RepresentableElement
from pyepidoc.shared.iterables import maxone
from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement

class _W(RepresentableElement):
    """
    Provides services for string representation of <w> elements.
    """

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)
        
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
            self._e, 
            element_classes, 
            'node'
        ) + ' '
    
    @property
    def leiden_str(self) -> str:
        return self.leiden_form

    @property
    def lemma(self) -> str | None:
        """
        Return the lemma of the <w> element.
        """
        return self.get_attr('lemma')
    
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
        
        inner_w = maxone(self._e.descendant_elements_by_local_name('w'), None, True)
        
        if inner_w is None:
            return
        
        inner_w.set_attr('id', xml_id, XMLNS)
        self._e.remove_attr('id', XMLNS, True)

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
            self._e, 
            element_classes, 
            'node'
        )
    
class W(_W):
    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'w':
            raise TypeError(f'Element should be <w> not {self._e.localname}.')