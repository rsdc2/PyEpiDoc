from __future__ import annotations
from pyepidoc.epidoc.edition_element import EditionElement


class Idno(EditionElement):
    """
    The <idno> element
    """

    @property
    def type(self) -> str | None:
        """
        The value of the @type attribute
        """
        return self.get_attrib('type')

    @property
    def value(self) -> str:
        """
        The text contents of the <idno> element
        """
        return self.text
    
    @value.setter
    def value(self, value: str) -> None:
        """
        Set the text content of the <idno> element
        """
        self.text = value