from __future__ import annotations
from typing import overload

from lxml import etree
from lxml.etree import _Element

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared.iterables import head
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.epidoc.epidoc_element import EpiDocElement
from pyepidoc.xml.xml_element import XmlElement


class Change(EpiDocElement):
    """
    The <respStmt> node, including collections of
    <respStmt>
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Change):
            raise TypeError(f'Cannot compare Change with {type(other)}')
        self.text
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

        :param when: Date string in format yyyy-mm-dd
        :param who: Identifier corresponding to the `@xml:id` attribute of the name 
        element in the <respStmt>, prefixed by `#`, e.g. for the initials 'JB', this value should be '#JB'
        :text: Free text to describe the change
        """

        elem = EpiDocElement.create_new('change', {
            'when': when,
            'who': who
        })
        elem.append_node(text)
        return Change(elem)
    
    @staticmethod
    def from_dict(dict: dict[str, str]) -> Change:
        return Change.from_details(dict['when'], dict['who'], dict['text'])

    @property
    def when(self) -> str | None:
        return self.get_attrib('when')
    
    @property
    def who(self) -> str | None:
        return self.get_attrib('who')