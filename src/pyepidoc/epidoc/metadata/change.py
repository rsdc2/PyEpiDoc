from __future__ import annotations
from typing import overload

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.utils import head
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.element import EpiDocElement
from pyepidoc.xml.baseelement import BaseElement


class Change(EpiDocElement):
    """
    The <respStmt> node, including collections of
    <respStmt>
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Change):
            raise TypeError(f'Cannot compare Change with {type(other)}')
        
        return self.who == other.who and \
            self.when == other.when and \
            self.text == other.text

    @staticmethod
    def from_details(
        when: str, 
        who: str, 
        text: str) -> Change:

        """
        Create a new Change from the details to be provided.
        """

        elem = EpiDocElement.create('change', {
            'when': when,
            'who': who
        })
        elem.append_element_or_text(text)
        return Change(elem)

    @property
    def when(self) -> str | None:
        return self.get_attrib('when')
    
    @property
    def who(self) -> str | None:
        return self.get_attrib('who')
    
    @property
    def text(self) -> str | None:
        return self.text
