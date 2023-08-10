from __future__ import annotations

from .element import Element
from ..xml.baseelement import BaseElement
from typing import Optional, Union
from lxml.etree import _Element 


class Lb(Element):    

    """
    Provides services for <lb> ('line break') elements.
    """

    def __init__(self, e: _Element | Element | BaseElement | None = None):
        type_err_msg = f'e should be _Element or Element type or None. Type is {type(e)}.'
        node_name_err_msg = f'Element must be <lb>. Element is {Element(e).local_name}.'

        if type(e) not in [_Element, Element, BaseElement] and e is not None:
            raise TypeError(type_err_msg)

        if type(e) is _Element:
            self._e = e
        elif type(e) is Element:
            self._e = e.e
        elif type(e) is BaseElement:
            self._e = e.e

        if self.local_name != 'lb':
            raise TypeError(node_name_err_msg)

    def __repr__(self):
        
        content = ''.join([
            "n: ",
            self.n, 
            f"{f', break: {self.break_value}' if self.break_value is not None else ''}"
        ])

        return f"Lb({content})"

    @property
    def break_value(self) -> Optional[str]:
        return self.get_attrib('break')

    @property
    def line_elems(self):
        pass

    @property
    def line_text(self) -> Optional[str]:
        pass

    @property
    def n(self) -> Optional[str]:
        """
        Returns the 'n' attribute of the <lb> element.
        """

        return self.get_attrib('n')
