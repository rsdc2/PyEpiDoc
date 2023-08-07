from __future__ import annotations

from typing import Optional, Union
from lxml.etree import _Element

from ..base import Element, BaseElement
from ..utils import head, flatlist

from .ex import Ex
from .abbr import Abbr
from .am import Am
from .epidoctypes import AbbrType


class Expan(Element):

    """
    Provides services for <expan> elements in EpiDoc XML.
    Will normally contain <abbr> and <ex> elements.
    """

    def __init__(self, e:Optional[_Element]=None):
        if type(e) is not _Element and e is not None:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if self.tag.name != 'expan':
            raise TypeError('Element should be of type <expan>.')

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
        objs = [self.abbr_ex_or_am(elem) for elem in self.desc_elems
            if elem.local_name in ['ex', 'abbr']]

        return ''.join([str(obj) for obj in objs])

    @property
    def abbr(self) -> list[Abbr]:
        return [Abbr(elem.e) for elem in self.abbr_elems]        

    @property
    def as_element(self) -> Element:
        return Element(self.e)

    @property
    def first_abbr(self) -> Optional[Abbr]:
        return head(self.abbr)

    @property
    def abbr_count(self) -> int:
        return len(self.abbr_elems)

    @property
    def am(self) -> list[Am]:
        return flatlist([abbr.am for abbr in self.abbr])

    @property
    def am_count(self) -> int:
        return len(self.am_elems)

    @staticmethod
    def abbr_ex_or_am(elem: BaseElement) -> Optional[Union[Abbr, Ex, Am]]:

        element_classes: dict[str, type] = {
            'ex': Ex,
            'abbr': Abbr,
            'am': Am
        }

        tag = elem.local_name
        cls = element_classes.get(tag, None)

        if cls is None:
            return None

        return cls(elem.e)

    @property
    def abbr_type(self) -> AbbrType:

        if self.first_abbr is not None:
            if self.first_abbr.is_multiplicative:
                return AbbrType.multiplication  

        if len(self.abbr) == 1 and len(self.ex) == 1:
            return AbbrType.suspension

        if len(self.abbr) > 1:

            if self.last_child is not None:
                last_child_type = type(self.abbr_ex_or_am(self.last_child))
                
                if last_child_type is Abbr:
                    return AbbrType.contraction
                elif last_child_type is Ex:
                    return AbbrType.contraction_with_suspension


        return AbbrType.unknown

    @property
    def ex_count(self) -> int:
        return len(self.ex_elems)

    @property
    def ex(self) -> list[Ex]:
        return [Ex(elem.e) for elem in self.ex_elems]        

