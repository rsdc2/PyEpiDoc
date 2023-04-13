from typing import Optional
from lxml.etree import _Element # type: ignore
from ..base import Element


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

    @property
    def abbr_count(self) -> int:
        return len(self.abbr_elements)

    @property
    def ex_count(self) -> int:
        return len(self.ex)
