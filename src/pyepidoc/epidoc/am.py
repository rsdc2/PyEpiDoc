from __future__ import annotations

from .element import EpiDocElement
from pyepidoc.epidoc.utils import descendant_text
from typing import Optional

class Am(EpiDocElement):    

    """
    Provides services for <am> ('abbreviation marker') elements.
    See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html
    last accessed 2023-04-13.
    """

    def __str__(self) -> str:

        return ''.join([
            '{',
            self.text_desc_compressed_whitespace,
            '}'
        ])

    @property
    def first_char(self) -> Optional[str]:
        # .strip() is used to exclude cases where there is text, 
        # but is whitespace
        text = self.text_desc_compressed_whitespace.strip()
        if len(text) > 0:
            return text[0]

        return None
