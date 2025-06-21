from __future__ import annotations
from typing import overload

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.utils import head
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.xml.xml_element import XmlElement


class Idno(EpiDocElement):
    """
    The <idno> element
    """

    @property
    def type(self) -> str | None:
        """
        The value of the @type attribute
        """
        return self.get_attrib('type')
    
    @property
    def value(self) -> str | None:
        """
        The text contents of the <idno> element
        """
        return self.text
    
    @value.setter
    def value(self, value: str) -> None:
        """
        Set the text content of the <idno> element
        """
        self.text = value