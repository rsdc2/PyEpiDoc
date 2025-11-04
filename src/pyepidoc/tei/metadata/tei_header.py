from __future__ import annotations
from pyepidoc.epidoc.edition_element import EditionElement
from .file_desc import FileDesc
from .revision_desc import RevisionDesc


class TeiHeader(EditionElement):
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
        Add a new <fileDesc> element to the <teiHeader> element
        """
        if self.file_desc is not None:
            raise Exception('<fileDesc> already exists on <teiHeader>')
        file_desc_elem = EditionElement.create_new(localname='fileDesc')
        self.e.append(file_desc_elem.e)

        return self
    
    def append_new_revision_desc(self) -> TeiHeader:

        """
        Add a new <revisionDesc> element to the <teiHeader> element
        """
        if self.revision_desc is not None:
            raise Exception('<revisionDesc> already exists on <teiHeader>')
        revision_desc = RevisionDesc.create()
        self.append_node(revision_desc)
        return self
    
    @staticmethod
    def create() -> TeiHeader:
        """
        Create a new <teiHeader> element, but do not
        append it to its host document
        """
        tei_header_elem = EditionElement.create_new('teiHeader')
        return TeiHeader(tei_header_elem)
    
    def ensure_revision_desc(self) -> RevisionDesc:
        if self.revision_desc is None:
            self.append_new_revision_desc()

        assert self.revision_desc is not None
        return self.revision_desc

    @property
    def file_desc(self) -> FileDesc | None:
        """
        The <titleStmt> element of the document,
        providing details including a series of 
        <respStmt>
        """

        file_desc_elem = self.get_descendant_tei_element(
            'fileDesc', 
            throw_if_more_than_one=True
        )
        
        if file_desc_elem is None:
            return None
        
        return FileDesc(file_desc_elem)

    @property
    def revision_desc(self) -> RevisionDesc | None:
        revision_desc = self.get_descendant_tei_element(
            'revisionDesc', 
            throw_if_more_than_one=True
        )
        
        if revision_desc is None:
            return None
                
        return RevisionDesc(revision_desc)