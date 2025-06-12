from __future__ import annotations
from pyepidoc.epidoc.element import EpiDocElement
from .change import Change

class ListChange(EpiDocElement):

    def append_change(self, change: Change) -> ListChange:
        """
        Append a <change> element to the <listChange>
        """
        self.append_element_or_text(change)
        return self

    @property
    def changes(self) -> list[Change]:
        children = self.child_elems
        return list(map(lambda child: Change(child), children))

    @staticmethod
    def create_new():
        elem = EpiDocElement.create_new('listChange')
        return ListChange(elem)
    
    @staticmethod
    def from_epidoc_element(element: EpiDocElement):
        if element.localname != 'listChange':
            raise Exception('Element localname must be "listChange"')
        
        return ListChange(element)