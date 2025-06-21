from __future__ import annotations
from typing import overload

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.utils import head
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.xml.xml_element import XmlElement
from .idno import Idno

class PublicationStmt(EpiDocElement):
    """
    The <respStmt> node, including collections of
    <respStmt>
    """

    @property
    def idnos(self) -> list[Idno]:

        return self.get_child_tokens()
