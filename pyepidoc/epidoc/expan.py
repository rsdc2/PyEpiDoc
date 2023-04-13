from __future__ import annotations

from typing import Optional, Union
from lxml.etree import _Element # type: ignore
from ..base import Element
from ..base.namespace import Namespace

from .ex import Ex
from .abbr import Abbr


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

        return f"Expan({content})>"

    def __str__(self) -> str:
        objs = [self.abbr_or_expan(elem) for elem in self.desc_elems
            if elem.name_no_namespace in ['ex', 'abbr']]

        return ''.join([str(obj) for obj in objs])

    @property
    def abbr(self) -> list[Abbr]:
        return [Abbr(elem) for elem in self.abbr_elems]        

    @property
    def abbr_count(self) -> int:
        return len(self.abbr_elems)

    @property
    def ex_count(self) -> int:
        return len(self.ex_elems)

    @property
    def ex(self) -> list[Ex]:
        return [Ex(elem) for elem in self.ex_elems]        

    @staticmethod
    def abbr_or_expan(elem: Element) -> Optional[Union[Expan, Abbr ,Ex]]:

        element_classes: dict[str, type] = {
            'ex': Ex,
            'abbr': Abbr
        }

        tag = elem.name_no_namespace
        cls = element_classes.get(tag, None)

        if cls is None:
            return None

        return cls(elem.e)