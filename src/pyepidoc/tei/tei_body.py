from __future__ import annotations
from lxml.etree import _Element

from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.shared.namespaces import TEINS

from .tei_div1 import TeiDiv1 as Div1

class TeiBody(TeiElement):    

    """
    Provides services for the <body> element of the EpiDoc file
    """

    def __init__(self, e: _Element | TeiElement | XmlElement) -> None:
        
        super().__init__(e)
        body_tag = ns.give_ns('body', TEINS)

        if self._e.tag != body_tag:
            raise ValueError(f'Cannot make <body> element from '
                             f'<{self._e.tag}> element.')

    @property
    def div1s(self) -> list[Div1]:
        return [Div1(child) for child in self._e.child_elements
                if child.localname == 'div1']
