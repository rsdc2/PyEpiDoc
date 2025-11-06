from __future__ import annotations
from pyepidoc.epidoc.edition_element import EditionElement
from .change import Change

class ListChange(EditionElement):

    def append_change(self, change: Change) -> ListChange:
        """
        Append a <change> element to the <listChange>
        """
        self.append_node(change)
        return self

    @property
    def changes(self) -> list[Change]:
        children = self.child_elems
        return list(map(lambda child: Change(child), children))

    @staticmethod
    def create():
        elem = EditionElement.create('listChange')
        return ListChange(elem)
    
    @staticmethod
    def from_epidoc_element(element: EditionElement):
        if element.localname != 'listChange':
            raise Exception('Element localname must be "listChange"')
        
        return ListChange(element)