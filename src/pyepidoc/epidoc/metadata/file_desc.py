from __future__ import annotations
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from .title_stmt import TitleStmt
from .publication_stmt import PublicationStmt

class FileDesc(EpiDocElement):
    """
    The <fileDesc> element
    """

    def append_title_stmt(
        self,
        title_stmt: TitleStmt
    ) -> TitleStmt:
        
        if self.title_stmt is not None:
            raise ValueError('Cannot append <titleStmt> since there is already one '
                             'present in the document')
        
        if title_stmt.localname != 'titleStmt':
            raise TypeError('The element to append is not a <titleStmt> element'
                            f'but a <{title_stmt.localname}> element')
        
        self.append_node(title_stmt)

        if self.title_stmt is None:
            raise Exception('Failed to append <titleStmt>')
        
        return self.title_stmt

    def append_new_publication_stmt(self) -> PublicationStmt:
        """
        Add a new <respStmt> element to the <titleStmt/> element
        """
        if self.publication_stmt is not None:
            raise ValueError('Cannot append <publicationStmt> since there is already '
                             'one present in the document')
        
        publication_stmt = EpiDocElement.create_new('publicationStmt')
        self.append_node(publication_stmt)
        
        if self.publication_stmt is None:
            raise TypeError('Failed to add <publicationStmt> element')
        
        return self.publication_stmt
    
    def ensure_publication_stmt(self) -> PublicationStmt:
        """
        Returns the <publicationStmt> if it exists, otherwise
        appends a new <publicationStmt>
        """
        if self.publication_stmt is None:
            return self.append_new_publication_stmt()
        return self.publication_stmt

    def ensure_title_stmt(self) -> TitleStmt:
        """
        Returns the <publicationStmt> if it exists, otherwise
        appends a new <publicationStmt>
        """
        if self.title_stmt is None:
            title_stmt = TitleStmt(EpiDocElement.create_new('titleStmt'))
            return self.append_title_stmt(title_stmt)

        return self.title_stmt

    @property
    def publication_stmt(self) -> PublicationStmt | None:
        """
        The <publicationStmt> element of the document,
        providing details including a series of 
        <idno>
        """

        publication_stmt_elem = self.get_descendant_tei_element(
            'publicationStmt', 
            throw_if_more_than_one=True
        )
        
        if publication_stmt_elem is None:
            return None
        
        return PublicationStmt(publication_stmt_elem)

    @property
    def title_stmt(self) -> TitleStmt | None:
        """
        The <titleStmt> element of the document,
        providing details including a series of 
        <respStmt>
        """

        title_stmt_elem = self.get_descendant_tei_element(
            'titleStmt', 
            throw_if_more_than_one=True
        )
        
        if title_stmt_elem is None:
            return None
        
        return TitleStmt(title_stmt_elem)

