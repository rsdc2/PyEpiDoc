from ..base import Element
from typing import Optional

class Am(Element):    

    """
    Provides services for <am> ('abbreviation marker') elements.
    See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html
    last accessed 2023-04-13.
    """

    def __str__(self) -> str:
        return ''.join([
            '[',
            self.text_desc_compressed_whitespace.strip(),
            ']',
            f"{'' if self.tail is None else self.tail.strip()}"
        ])

    @property
    def first_char(self) -> Optional[str]:
        if len(self.text_desc_compressed_whitespace.strip()) > 0:
            return self.text_desc_compressed_whitespace[0]

        return None
