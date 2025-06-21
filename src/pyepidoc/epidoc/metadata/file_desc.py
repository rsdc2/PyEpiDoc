from __future__ import annotations
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from .title_stmt import TitleStmt


class FileDesc(EpiDocElement):
    """
    The <fileStmt> element
    """

    def append_title_stmt(
        self,
        title_stmt: TitleStmt
    ) -> FileDesc:
        
        self.e.append(title_stmt.e)
        return self

    def append_new_title_stmt(self, title: str) -> FileDesc:

        """
        Add a new <respStmt> element to the <titleStmt/> element
        """
        title_stmt = TitleStmt.from_details(title)
        self.append_title_stmt(title_stmt)

        return self

    @property
    def title_stmt(self) -> TitleStmt | None:
        """
        The <titleStmt> element of the document,
        providing details including a series of 
        <respStmt>
        """

        title_stmt_elem = self.get_desc_tei_elem(
            'titleStmt', 
            throw_if_more_than_one=True
        )
        
        if title_stmt_elem is None:
            return None
        
        return TitleStmt(title_stmt_elem)

