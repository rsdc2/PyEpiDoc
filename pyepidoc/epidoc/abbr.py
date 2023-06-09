from __future__ import annotations

from typing import Optional
from ..base import Element
from ..utils import head
from .am import Am


class Abbr(Element):    
    def __str__(self) -> str:
        ams = [Am(elem.e) for elem in self.desc_elems
            if elem.name_no_namespace == 'am']

        return self.text.strip() + ''.join([str(am) for am in ams])

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
        

class AbbrInfo:

    _form:Optional[str]
    _abbr:Optional[str]

    def __init__(self, 
        form:Optional[str]=None, 
        abbr:Optional[str]=None, 
    ):
        self._form = form.lower() if form is not None else None
        self._abbr = abbr.lower() if abbr is not None else None

    @property
    def form(self):
        if self._form is None:
            return ''
        return self._form.strip()
    
    @property
    def abbr(self):
        return self._abbr

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if type(other) is AbbrInfo:
            return str(self) == str(other)
        
        return False

    def __str__(self) -> str:
        return f'Form: {self.form}; Abbr: {self.abbr}'

    def __repr__(self) -> str:
        return f'AbbrInfo({self.__str__()})'
