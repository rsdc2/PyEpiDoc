from __future__ import annotations

from typing import Optional
from .element import EpiDocElement
from ..utils import head
from .am import Am


class Abbr(EpiDocElement):    
    def __str__(self) -> str:
        ams = [Am(elem.e) for elem in self.desc_elems
            if elem.local_name == 'am']

        return self.text_desc.strip() + ''.join([str(am) for am in ams])

    @property
    def am(self) -> list[Am]:
        return [Am(elem.e) for elem in self.am_elems]

    @property
    def am_count(self) -> int:
        return len(self.am_elems)

    @property
    def first_am(self) -> Optional[Am]:
        return head(self.am)

    @property
    def first_char(self) -> Optional[str]:
        if len(self.text_desc_compressed_whitespace.strip()) > 0:   
            # .strip() is used to exclude cases where there is text, but is whitespace
            return self.text_desc_compressed_whitespace[0]

        return None

    @property
    def is_multiplicative(self) -> bool:
        if self.first_am is None:
            return False

        if self.first_char == self.first_am.first_char:
            if self.first_char is not None:
                return True
            
        return False
        
