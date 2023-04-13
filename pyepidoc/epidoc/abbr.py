from typing import Optional
from ..base import Element

class Abbr(Element):    
    def __str__(self) -> str:
        return self.text_desc_compressed_whitespace




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
