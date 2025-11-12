from __future__ import annotations
from typing import override
from pyepidoc.tei.tei_element import TeiElement
from .change import Change
from .list_change import ListChange


class RevisionDesc(TeiElement):
    """
    The <revisionDesc> element
    """
    
    def append_change(self, change: Change) -> RevisionDesc:
        """
        Append a <change> element to the <listChange>
        """
        self.list_change.append_change(change)
        return self

    @override
    @classmethod
    def create(
            cls      
        ) -> RevisionDesc:
        """
        Create a new <revisionDesc> element with an empty <listChange> 
        """
        revision_desc = RevisionDesc(TeiElement.create('revisionDesc'))
        list_change = ListChange.create()
        revision_desc.append_node(list_change)
        return revision_desc
    
    def from_epidoc_element(element: TeiElement) -> RevisionDesc:
        if element.localname != 'revisionDesc':
            raise Exception('Element must have localname "revisionDesc"')
        
        return RevisionDesc(element)
        
    @property
    def list_change(self) -> ListChange:
        """
        Element containing the changes to the document
        """

        list_change = self.get_descendant_tei_element(
            'listChange', 
            throw_if_more_than_one=True
        )
        
        if list_change is None:
            raise Exception('No <listChange> element present in <revisionDesc>')
        
        return ListChange.from_tei_element(TeiElement(list_change))

