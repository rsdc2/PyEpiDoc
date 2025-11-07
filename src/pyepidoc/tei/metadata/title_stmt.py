from __future__ import annotations

from pyepidoc.tei.tei_element import TeiElement
from .resp_stmt import RespStmt


class TitleStmt(TeiElement):
    """
    The <titleStmt> node, including collections of <respStmt>
    """

    def append_resp_stmt(
            self,
            resp_stmt: RespStmt
        ) -> TitleStmt:

        """
        Append `<respStmt>` if `@resp` value does not already exist on document.
        """
        if resp_stmt.resp is None:
            raise TypeError('resp_stmt value cannot be None')
        if resp_stmt.initials is None:
            raise TypeError('resp_stmt.initials cannot be None ')
        if not self.has_resp_initials(resp_stmt.initials):
            self.e.append(resp_stmt.e)
        return self

    def append_new_resp_stmt(
        self,
        name: str, 
        initials: str, 
        ref: str, 
        resp_text: str) -> TitleStmt:

        """
        Add a new `<respStmt>` element to the `<titleStmt>` element
        """
        resp_stmt = RespStmt.from_details(name, initials, ref, resp_text)
        self.append_resp_stmt(resp_stmt)

        return self
    
    @staticmethod
    def from_details(title: str) -> TitleStmt:
        title_elem = TeiElement.create('titleStmt')
        title_elem.text = title
        return TitleStmt(title_elem)

    @property
    def resp_stmts(self) -> list[RespStmt]:
        """
        Return all the <resp/> statements
        """
        
        resp_stmt_elems = self.descendant_elements_by_local_name("respStmt")
        return list(map(RespStmt.from_element, resp_stmt_elems))
    
    def has_resp_initials(self, resp_initials: str) -> bool:
        for resp_stmt in self.resp_stmts:
            if resp_stmt.initials == resp_initials:
                return True
            
        return False


    
