from __future__ import annotations

from ..edition_element import EditionElement
from pyepidoc.epidoc.utils import descendant_text
from typing import Optional

class Am(EditionElement):    

    """
    Provides services for <am> ('abbreviation marker') elements.
    See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html
    last accessed 2023-04-13.
    """

    @property
    def first_char(self) -> Optional[str]:
        # .strip() is used to exclude cases where there is text, 
        # but is whitespace
        text = self.text_desc_compressed_whitespace.strip()
        if len(text) > 0:
            return text[0]

        return None

    @property
    def leiden_form(self) -> str:

        return ''.join([
            '{',
            self.text_desc_compressed_whitespace,
            '}'
        ])

    @property
    def normalized_form(self) -> str:
        return ''