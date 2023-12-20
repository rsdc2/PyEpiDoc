from __future__ import annotations

from typing import Optional
from itertools import chain

from lxml.etree import _Element

from ..utils import head

from .element import EpiDocElement

from .ex import Ex
from .abbr import Abbr
from .am import Am

from .epidoc_types import AbbrType
from .utils import leiden_str_from_children, callable_from_localname, local_name


class Expan(EpiDocElement):

    """
    Provides services for <expan> elements in EpiDoc XML.
    Will normally contain <abbr> and <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if local_name(e) != 'expan':
            raise TypeError(f'Element should be of type <expan>, '
                            f'but is of type <{local_name(e)}>.')

    def __repr__(self):
        tail = '' if self.tail is None else self.tail
        content = ''.join([
            "'",
            str(self),
            "'",
            f"{'; tail: ' if tail.strip() != '' else ''}", 
            tail.strip()]
        )

        return f"Expan({content})"

    def __str__(self) -> str:
        return self.leiden

    @property
    def abbr(self) -> list[Abbr]:
        return [Abbr(elem.e) for elem in self.abbr_elems]        

    @property
    def abbr_count(self) -> int:
        return len(self.abbr_elems)

    @property
    def abbr_type(self) -> AbbrType:

        if self.first_abbr is not None:
            if self.first_abbr.is_multiplicative:
                return AbbrType.multiplication  

        if len(self.abbr) == 1 and len(self.ex) == 1:
            return AbbrType.suspension

        if len(self.abbr) > 1:

            if self.last_child is not None:
                last_child_type = type(callable_from_localname(self.last_child.e, self.element_classes))
                
                if last_child_type is Abbr:
                    return AbbrType.contraction
                elif last_child_type is Ex:
                    return AbbrType.contraction_with_suspension

        return AbbrType.unknown

    @property
    def am(self) -> list[Am]:
        return list(chain(*[abbr.am for abbr in self.abbr]))

    @property
    def am_count(self) -> int:
        return len(self.am_elems)
    
    @property
    def as_element(self) -> EpiDocElement:
        return EpiDocElement(self.e)

    @property
    def first_abbr(self) -> Optional[Abbr]:
        return head(self.abbr)

    @property
    def element_classes(self) -> dict[str, type]:
        from .abbr import Abbr
        from .am import Am
        from .ex import Ex
        from .lb import Lb
        from .supplied import Supplied

        element_classes: dict[str, type] = {
            'abbr': Abbr,
            'am': Am,
            'ex': Ex,
            'lb': Lb,
            'supplied': Supplied
        }

        return element_classes

    @property
    def ex_count(self) -> int:
        return len(self.ex_elems)

    @property
    def ex(self) -> list[Ex]:
        return [Ex(elem.e) for elem in self.ex_elems]

    @property
    def leiden(self) -> str:
        
        """
        Returns a Leiden-formatted string representation
        of the <expan> element
        """

        return leiden_str_from_children(self.e, self.element_classes, 'element')