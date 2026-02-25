from __future__ import annotations

from pyepidoc.epidoc.tokenizable_element import TokenizableElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.shared.enums import AtomicTokenType
from typing import Optional


class Lb(TokenizableElement):    

    """
    Provides services for <lb> ('line break') elements.
    """

    def __init__(self, e: TokenizableElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'lb':
            node_name_err_msg = f'Element must be <lb>. Element is {TokenizableElement(e)._e.localname}.'
            raise TypeError(node_name_err_msg)

    def __repr__(self):
        
        content = ''.join([
            "n: ",
            self.n if self.n is not None else 'None', 
            f"{f', break: {self.break_value}' if self.break_value is not None else ''}"
        ])

        return f"Lb({content})"
    
    @property
    def break_value(self) -> Optional[str]:
        return self.get_attr('break')

    @property
    def leiden_form(self) -> str:
        if self._e.has_ancestors_by_names(AtomicTokenType.values()):
            return '|'
        return '|'

    @property
    def line_elems(self):
        pass

    @property
    def line_text(self) -> Optional[str]:
        pass

    @property
    def n(self) -> Optional[str]:
        """
        Returns the 'n' attribute of the <lb> element.
        """

        return self.get_attr('n')

    @property
    def normalized_form(self) -> str:
        return ''
