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
    def abbrs(self) -> list[Abbr]:
        """
        Returns a list of <abbr> Elements
        """
        return [Abbr(elem.e) for elem in self.abbr_elems]        

    @property
    def abbr_count(self) -> int:
        return len(self.abbr_elems)

    @property
    def abbr_type(self) -> AbbrType:

        if self.is_multiplicative:
            return AbbrType.multiplication  

        if self.is_suspension:
            return AbbrType.suspension

        if len(self.abbrs) > 1:

            if self.last_child is not None:
                last_child_type = type(callable_from_localname(self.last_child.e, self.element_classes))
                
                if last_child_type is Abbr:
                    return AbbrType.contraction
                elif last_child_type is Ex:
                    return AbbrType.contraction_with_suspension

        return AbbrType.unknown

    @property
    def am(self) -> list[Am]:
        return list(chain(*[abbr.am for abbr in self.abbrs]))

    @property
    def am_count(self) -> int:
        return len(self.am_elems)
    
    @property
    def as_element(self) -> EpiDocElement:
        return EpiDocElement(self.e)

    @property
    def first_abbr(self) -> Optional[Abbr]:
        return head(self.abbrs)

    @property
    def element_classes(self) -> dict[str, type]:
        from .abbr import Abbr
        from .am import Am
        from .ex import Ex
        from .hi import Hi
        from .lb import Lb
        from .supplied import Supplied

        element_classes: dict[str, type] = {
            'abbr': Abbr,
            'am': Am,
            'ex': Ex,
            'hi': Hi, 
            'lb': Lb,
            'supplied': Supplied
        }

        return element_classes

    @property
    def ex_count(self) -> int:
        return len(self.ex_elems)

    @property
    def exs(self) -> list[Ex]:
        return [Ex(elem.e) for elem in self.ex_elems]

    @property
    def first_desc_text_node(self) -> str:
        xpath = 'descendant::text()[position()=1]'
        return ''.join(map(str, self.xpath(xpath)))

    def first_desc_textnode_is_desc_of(self, localname: str) -> bool:
        first_desc_node_xpath = 'descendant::text()[position()=1]'
        first_desc_of_abbr_xpath = f'descendant::text()[ancestor::ns:{localname}][position()=1]'

        xpath = ' = '.join([first_desc_node_xpath, first_desc_of_abbr_xpath])

        return self.xpath_bool(xpath)


    @property
    def is_contraction(self) -> bool:
        """
        Returns True if:
            - There is more than one <abbr>
            - The first descendant text node is a descendant of <abbr>
            - The last descendant text node is a descendant of <abbr>
            - The first descendant text node is not a descendant of <am>
            - These two <abbr> nodes are not the same 
        """

        if self.abbr_count < 2:
            return False
        
        return self.first_desc_textnode_is_desc_of('abbr') and \
            self.last_desc_textnode_is_desc_of('abbr') and \
            not self.first_desc_textnode_is_desc_of('am')

    @property
    def is_multiplicative(self) -> bool:
        return any([abbr.is_multiplicative for abbr in self.abbrs])

    @property
    def is_suspension(self) -> bool:
        return len(self.abbrs) == 1 and len(self.exs) == 1

    @property
    def last_desc_text_node(self) -> str:
        xpath = 'descendant::text()[position()=last()]'
        return ''.join(map(str, self.xpath(xpath)))

    def last_desc_textnode_is_desc_of(self, localname: str) -> bool:
        last_desc_node_xpath = 'descendant::text()[postion()=last()]'
        last_desc_of_abbr_xpath = f'descendant::text()[ancestor::ns:{localname}][position()=last()]'

        xpath = ' = '.join([last_desc_node_xpath, last_desc_of_abbr_xpath])

        return self.xpath_bool(xpath)

    @property
    def leiden(self) -> str:
        
        """
        Returns a Leiden-formatted string representation
        of the <expan> element
        """

        return leiden_str_from_children(self.e, self.element_classes, 'element')