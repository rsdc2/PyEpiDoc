from __future__ import annotations
from pyepidoc.tei.tei_element import TeiElement
from .change import Change

class ListChange(TeiElement):

    def append_change(self, change: Change) -> ListChange:
        """
        Append a <change> element to the <listChange>
        """
        self._e.append_node(change)
        return self

    @property
    def changes(self) -> list[Change]:
        children = self.child_elems
        return list(map(lambda child: Change(child), children))

    @staticmethod
    def create():
        elem = TeiElement.create('listChange')
        return ListChange(elem)
    
    @staticmethod
    def from_tei_element(element: TeiElement):
        if element._e.localname != 'listChange':
            raise ValueError('Element localname must be "listChange"')
        
        return ListChange(element)