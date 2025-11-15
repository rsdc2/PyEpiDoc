from __future__ import annotations
from typing import Literal

from lxml import etree
from lxml.etree import _Element

from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.metadata.resp_stmt import RespStmt
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.token import Token

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.enums import (
    StandoffEditionElements, 
    ContainerStandoffEditionType
)
from pyepidoc.shared.iterables import maxone, listfilter
from pyepidoc.shared.dicts import dict_remove_none


class TeiBody(TeiElement):    

    """
    Provides services for the <body> element of the EpiDoc file
    """

    def __init__(
        self, 
        e: _Element | TeiElement | XmlElement
    ) -> None:
        
        super().__init__(e)
        body_tag = ns.give_ns('body', TEINS)

        if e.e.tag != body_tag:
            raise ValueError(f'Cannot make <body> element from '
                             f'<{self.tag}> element.')
