from __future__ import annotations

from typing import Optional

from ...utils import head

from ..element import EpiDocElement
from ..utils import leiden_str_from_children, normalized_str_from_children
from .am import Am

class Abbr(EpiDocElement):    
    def __str__(self) -> str:

        return self.leiden_form

    @property
    def am(self) -> list[Am]:
        return [Am(elem.e) for elem in self.am_elems]

    @property
    def am_count(self) -> int:
        return len(self.am_elems)

    @property
    def _element_classes(self) -> dict[str, type]:
        from .choice import Choice
        from .hi import Hi
        from .lb import Lb
        from .unclear import Unclear

        element_classes: dict[str, type] = {
            'am': Am,
            'choice': Choice,
            'hi': Hi,
            'lb': Lb,
            'unclear': Unclear
        }

        return element_classes
    
    @property
    def first_am(self) -> Optional[Am]:
        return head(self.am)

    @property
    def first_non_am_char(self) -> Optional[str]:
        child_text_nodes = self.xpath('descendant::text()[not(ancestor::ns:am)]')

        text = ''.join(map(str, child_text_nodes))
        
        if text == '':
            return None
        
        return text[0]

    @property
    def is_multiplicative(self) -> bool:

        """
        Returns true if the abbreviation is multiplicative
        i.e. where there is a repetition of one or more
        abbreviation markers
        """

        if self.first_am is None:
            return False
        
        if self.first_non_am_char is None:
            return False
        
        if self.first_am.first_char is None:
            return False

        if self.first_non_am_char.lower() == self.first_am.first_char.lower():
            return True
        
        if self.last_non_am_char_before_am is None:
            return False
            
        if self.last_non_am_char_before_am.lower() == self.first_am.first_char.lower():
            return True
            
        return False

    @property
    def last_non_am_char_before_am(self) -> Optional[str]:
        child_text_nodes = self.xpath('descendant::text()[not(ancestor::ns:am) and following-sibling::ns:am]')

        text = ''.join(map(str, child_text_nodes))
        
        if text == '':
            return None
        
        return text[-1]

    @property
    def leiden_form(self) -> str:

        return leiden_str_from_children(
            self.e,
            self._element_classes,
            'node'
        )

    @property
    def normalized_form(self) -> str:
        
        return normalized_str_from_children(
            self.e,
            self._element_classes,
            'node'
        )
        if len(normalized) > 0:
            if normalized[0] == normalized[0].capitalize():
                return normalized.capitalize()

        return normalized