from __future__ import annotations
from pyepidoc.epidoc.element import EpiDocElement
from .change import Change
from .list_change import ListChange

class RevisionDesc(EpiDocElement):
    """
    The <revisionDesc> element
    """
    
    def append_change(self, change: Change) -> RevisionDesc:
        """
        Append a <change> element to the <listChange>
        """
        self.list_change.append_change(change)
        return self

    @staticmethod
    def create() -> RevisionDesc:
        """
        Create a new <revisionDesc> element with an empty <listChange> 
        """
        revision_desc = RevisionDesc(EpiDocElement.create('revisionDesc'))
        list_change = ListChange.create()
        revision_desc.append_element_or_text(list_change)
        return revision_desc
    
    def from_epidoc_element(element: EpiDocElement) -> RevisionDesc:
        if element.localname != 'revisionDesc':
            raise Exception('Element must have localname "revisionDesc"')
        
        return RevisionDesc(element)
        
    @property
    def list_change(self) -> ListChange:
        """
        Element containing the changes to the document
        """

        list_change = self.get_desc_tei_elem(
            'listChange', 
            throw_if_more_than_one=True
        )
        
        if list_change is None:
            raise Exception('No <listChange> element present in <revisionDesc>')
        
        return ListChange.from_epidoc_element(list_change)

