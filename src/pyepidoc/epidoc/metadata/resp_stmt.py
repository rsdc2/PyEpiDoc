from __future__ import annotations

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.element import EpiDocElement


class RespStmt(EpiDocElement):
    """
    The <respStmt> node, including collections of
    <respStmt>
    """

    @classmethod
    def new_resp_stmt(
        cls,
        name: str, 
        initials: str, 
        ref: str, 
        resp_text: str) -> RespStmt:

        """
        Create a new RespStmt element from the supplied details
        """
        resp_stmt_elem = cls.resp_stmt()
        name_elem = cls.name(name, initials, ref)
        resp_elem = cls.resp(resp_text)
        resp_stmt_elem.append(name_elem)
        resp_stmt_elem.append(resp_elem)
        return RespStmt(resp_stmt_elem)

    @staticmethod
    def name(name: str, initials: str, ref: str) -> _Element:
        """
        Create a new <name/> element
        """
        tag = ns.give_ns("name", TEINS)
        elem: _Element = etree.Element(tag)
        epidoc_elem = EpiDocElement(elem)
        epidoc_elem.set_attrib("id", initials, XMLNS)
        epidoc_elem.set_attrib("ref", ref)
        epidoc_elem.text = name
        return epidoc_elem.e
    
    @staticmethod
    def resp(text: str) -> _Element:
        """
        Create the <resp/> element within the <respStmt/>
        """
        tag = ns.give_ns("resp", TEINS)
        elem: _Element = etree.Element(tag)
        elem.text = text
        return elem

    @staticmethod
    def resp_stmt() -> _Element:
        """
        Create the <respStmt/> element
        """
        tag = ns.give_ns("respStmt", TEINS)
        elem: _Element = etree.Element(tag) 
        return elem