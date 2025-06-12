from __future__ import annotations
from pyepidoc.epidoc.element import EpiDocElement
from .resp_stmt import RespStmt

class TitleStmt(EpiDocElement):
    """
    The <titleStmt> node, including collections of <respStmt>
    """

    def append_resp_stmt(
        self,
        resp_stmt: RespStmt
    ) -> TitleStmt:
        
        self.e.append(resp_stmt.e)
        return self

    def append_new_resp_stmt(
        self,
        name: str, 
        initials: str, 
        ref: str, 
        resp_text: str) -> TitleStmt:

        """
        Add a new <respStmt> element to the <titleStmt/> element
        """
        resp_stmt = RespStmt.from_details(name, initials, ref, resp_text)
        self.e.append(resp_stmt.e)

        return self
    
    @staticmethod
    def from_details(title: str) -> TitleStmt:
        title_elem = EpiDocElement.create_new('titleStmt')
        title_elem.text = title
        return TitleStmt(title_elem)

    @property
    def resp_stmts(self) -> list[RespStmt]:
        """
        Return all the <resp/> statements
        """
        
        resp_stmt_elems = self.desc_elems_by_local_name("respStmt")
        return list(map(RespStmt.from_element, resp_stmt_elems))

    
