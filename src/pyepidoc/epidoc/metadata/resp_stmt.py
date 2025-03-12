from __future__ import annotations
from typing import overload

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.utils import head
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.xml.baseelement import BaseElement


class RespStmt(EpiDocElement):
    """
    The <respStmt> node, including collections of
    <respStmt>
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RespStmt):
            raise TypeError(f'Cannot compare RespStmt with {type(other)}')
        
        return self.name == other.name and \
            self.initials == other.initials and \
            self.resp == other.resp and \
            self.ref == other.ref

    @staticmethod
    def from_details(
        name: str, 
        initials: str, 
        ref: str, 
        resp_text: str) -> RespStmt:

        resp_stmt_elem = RespStmt.create_resp_stmt()
        name_elem = RespStmt.create_name(name, initials, ref)
        resp_elem = RespStmt.create_resp(resp_text)
        resp_stmt_elem.append(name_elem)
        resp_stmt_elem.append(resp_elem)
        resp_stmt = RespStmt(resp_stmt_elem)
        return resp_stmt

    @staticmethod
    def from_elem(elem: BaseElement) -> RespStmt:
        if elem.localname != 'respStmt':
            raise ValueError(
                'Expected element with local name "respStmt", '
                f'but instead have {elem.localname}'
            )
        
        respStmt = RespStmt(elem)
        return respStmt

    @staticmethod
    def create_name(name: str, initials: str, ref: str) -> _Element:
        """
        Create a new <name> element
        """
        tag = ns.give_ns("name", TEINS)
        elem: _Element = etree.Element(tag)
        epidoc_elem = EpiDocElement(elem)
        epidoc_elem.set_attrib("id", initials, XMLNS)
        epidoc_elem.set_attrib("ref", ref)
        epidoc_elem.text = name
        return epidoc_elem.e
    
    @staticmethod
    def create_resp(text: str) -> _Element:
        """
        Create the <resp> element within the <respStmt/>
        """
        tag = ns.give_ns("resp", TEINS)
        elem: _Element = etree.Element(tag)
        elem.text = text
        return elem

    @staticmethod
    def create_resp_stmt() -> _Element:
        """
        Create the <respStmt> element
        """
        tag = ns.give_ns("respStmt", TEINS)
        elem: _Element = etree.Element(tag) 
        return elem
    
    @property
    def initials(self) -> str | None:
        name_elem = self.name_elem
        if name_elem is None:
            return None
        
        return name_elem.get_attrib('id', XMLNS)

    @property
    def name(self) -> str | None:
        if self.name_elem is None: return None
        return self.name_elem.text
    
    @property
    def name_elem(self) -> BaseElement | None:
        desc_elems = self.get_desc_tei_elems(['name'])
        return head(desc_elems)
    
    @property
    def ref(self) -> str | None:
        if self.name_elem is None:
            return None
        return self.name_elem.get_attrib('ref')

    @property
    def resp(self) -> str | None:
        if self.resp_elem is None:
            return None
        return self.resp_elem.text

    @property
    def resp_elem(self) -> BaseElement | None:
        desc_elems = self.get_desc_tei_elems(['resp'])
        return head(desc_elems)
