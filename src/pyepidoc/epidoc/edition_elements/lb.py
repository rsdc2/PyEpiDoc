from __future__ import annotations

from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.xml.xml_element import XmlElement
from typing import Optional, Union
from lxml.etree import _Element 


class Lb(EpiDocElement):    

    """
    Provides services for <lb> ('line break') elements.
    """

    def __init__(self, e: _Element | EpiDocElement | XmlElement):
        type_err_msg = f'e should be _Element or Element type or None. Type is {type(e)}.'
        node_name_err_msg = f'Element must be <lb>. Element is {EpiDocElement(e).localname}.'

        if type(e) not in [_Element, EpiDocElement, XmlElement]:
            raise TypeError(type_err_msg)

        if type(e) is _Element:
            self._e = e
        elif type(e) is EpiDocElement:
            self._e = e.e
        elif type(e) is XmlElement:
            self._e = e.e

        if self.localname != 'lb':
            raise TypeError(node_name_err_msg)

    def __repr__(self):
        
        content = ''.join([
            "n: ",
            self.n if self.n is not None else 'None', 
            f"{f', break: {self.break_value}' if self.break_value is not None else ''}"
        ])

        return f"Lb({content})"
    
    @property
    def break_value(self) -> Optional[str]:
        return self.get_attrib('break')

    @property
    def leiden_form(self) -> str:
        return '|'

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

    @property
    def normalized_form(self) -> str:
        return ''
