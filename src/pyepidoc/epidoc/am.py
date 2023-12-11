from __future__ import annotations

from .element import EpiDocElement
from typing import Optional

class Am(EpiDocElement):    

    """
    Provides services for <am> ('abbreviation marker') elements.
    See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html
    last accessed 2023-04-13.
    """

    def __str__(self) -> str:
        return ''.join([
            '(',
            ''.join(map(str, self.leiden_elems)),
            ')',
            f"{'' if self.tail is None else self.tail.strip()}"
        ])

    @property
    def first_char(self) -> Optional[str]:
        if len(self.text_desc_compressed_whitespace.strip()) > 0:
            # .strip() is used to exclude cases where there is text, but is whitespace
            return self.text_desc_compressed_whitespace[0]

        return None
