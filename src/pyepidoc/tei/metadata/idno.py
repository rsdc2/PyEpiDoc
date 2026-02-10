from __future__ import annotations
from pyepidoc.tei.tei_element import TeiElement


class Idno(TeiElement):
    """
    The <idno> element
    """

    @property
    def type(self) -> str | None:
        """
        The value of the @type attribute
        """
        return self.get_attr('type')

    @property
    def value(self) -> str:
        """
        The text contents of the <idno> element
        """
        return self._e.text or ''
    
    @value.setter
    def value(self, value: str) -> None:
        """
        Set the text content of the <idno> element
        """
        self._e.text = value