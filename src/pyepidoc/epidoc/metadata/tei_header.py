from __future__ import annotations
from pyepidoc.epidoc.element import EpiDocElement
from .file_desc import FileDesc
from .revision_desc import RevisionDesc


class TeiHeader(EpiDocElement):
    """
    The <teiHeader> element
    """

    def append_file_desc(
        self,
        file_desc: FileDesc
    ) -> TeiHeader:
        
        self.e.append(file_desc.e)
        return self

    def append_new_file_desc(self) -> TeiHeader:

        """
        Add a new <respStmt> element to the <titleStmt/> element
        """
        file_desc_elem = EpiDocElement.create(localname='fileDesc')
        self.e.append(file_desc_elem.e)

        return self
    
    @staticmethod
    def create_tei_header() -> TeiHeader:
        """
        Create a new <teiHeader> element, but do not
        append it to its host document
        """
        tei_header_elem = EpiDocElement.create('teiHeader')
        return TeiHeader(tei_header_elem)

    @property
    def file_desc(self) -> FileDesc | None:
        """
        The <titleStmt> element of the document,
        providing details including a series of 
        <respStmt>
        """

        file_desc_elem = self.get_desc_tei_elem(
            'fileDesc', 
            throw_if_more_than_one=True
        )
        
        if file_desc_elem is None:
            return None
        
        return FileDesc(file_desc_elem)

    @property
    def revision_desc(self) -> RevisionDesc:
        revision_desc = self.get_desc_tei_elem(
            'revisionDesc', 
            throw_if_more_than_one=True
        )
        
        if revision_desc is None:
            raise Exception('No <revisionDesc> element present in <teiHeader>')
        
        return RevisionDesc(revision_desc)