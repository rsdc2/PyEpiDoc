from __future__ import annotations

from typing import Optional, Literal, cast
from itertools import chain

from lxml.etree import _Element

from ...shared import head

from ..element import EpiDocElement

from .ex import Ex
from .abbr import Abbr
from .am import Am
from .g import G

from ..enums import AbbrType
from ..utils import (leiden_str_from_children, 
                     callable_from_localname, 
                     localname,
                     normalized_str_from_children)


class Expan(EpiDocElement):

    """
    Provides services for <expan> elements in EpiDoc XML.
    Will normally contain <abbr> and <ex> elements.
    """

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if localname(e) != 'expan':
            raise TypeError(f'Element should be of type <expan>, '
                            f'but is of type <{localname(e)}>.')

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
        return self.leiden_str

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
    def abbr_types(self) -> list[AbbrType]:
        abbr_types = []

        if self.is_multiplication:
            abbr_types.append(AbbrType.multiplication)  

        if self.is_suspension and not self.is_multiplication and not self.is_contraction_with_suspension:
            abbr_types.append(AbbrType.suspension)

        if self.is_contraction:
            abbr_types.append(AbbrType.contraction)

        if self.is_contraction_with_suspension:
            abbr_types.append(AbbrType.contraction_with_suspension)

        return abbr_types

    @property
    def am(self) -> list[Am]:
        return list(chain(*[abbr.am for abbr in self.abbrs]))

    @property
    def am_count(self) -> int:
        return len(self.am_elems)
    
    @property
    def as_element(self) -> EpiDocElement:
        return EpiDocElement(self.e)
    
    def contains_g(self, with_ref: str | None = None) -> bool:
        """
        Return True if contains a `<g>` element (optionally with the
        @ref attribute set)
        """    
        gs = map(G, map(lambda elem: elem.e, self.desc_elems_by_local_name('g')))
        if with_ref is None:
            return len(list(gs)) > 0
        
        return any(map(lambda g: g.ref == with_ref, gs))

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

    def _desc_text_node_parent(self, position: str) -> Optional[_Element]:
        xpath = f'descendant::text()[position()={position}]/parent::*'
        result = head(self.xpath(xpath))
        if result is None:
            return None
        return cast(_Element, result)

    def _desc_textnode_is_desc_of(self, position: str, localname: str) -> bool:
        desc_text_parent_xpath = f'descendant::text()[position()={position}]/parent::*'
        desc_text_parent_of_abbr_xpath = (f'descendant::text()[position()={position}][ancestor::ns:{localname}]/'
                                          f'parent::*')
              
        desc_text_parent_result = self.xpath(desc_text_parent_xpath)
        desc_text_parent_of_abbr_result = self.xpath(desc_text_parent_of_abbr_xpath)

        if desc_text_parent_result == []:
            return False
        
        if desc_text_parent_of_abbr_result == []:
            return False
        
        return self.xpath(desc_text_parent_of_abbr_xpath)[0] == \
            self.xpath(desc_text_parent_xpath)[0]

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
        
        return self._desc_textnode_is_desc_of('1', 'abbr') and \
            self._desc_textnode_is_desc_of('last()', 'abbr') and \
            not self._desc_textnode_is_desc_of('1', 'am') and \
            not (self._desc_text_node_parent('1') == self._desc_text_node_parent('last()'))
    
    @property
    def is_contraction_with_suspension(self) -> bool:
        """
        Returns True if:
            - There is more than one <abbr> 
            - There is more than one <ex>
            - The first descendant text node is a descendant of <abbr>
            - The last descendant text node is a descendant of <ex>
            - The first descendant text node is not a descendant of <am>
        """

        if self.abbr_count < 2 or self.ex_count < 2:
            return False
        
        return self._desc_textnode_is_desc_of('1', 'abbr') and \
            self._desc_textnode_is_desc_of('last()', 'ex') and \
            not self._desc_textnode_is_desc_of('1', 'am')
    
    @property
    def is_multiplication(self) -> bool:
        return any([abbr.is_multiplicative for abbr in self.abbrs])

    @property
    def is_suspension(self) -> bool:
        return len(self.abbrs) == 1 and len(self.exs) == 1

    @property
    def last_desc_text_node(self) -> str:
        xpath = 'descendant::text()[position()=last()]'
        return ''.join(map(str, self.xpath(xpath)))

    def last_desc_textnode_is_desc_of(self, localname: str) -> bool:
        first_desc_of_abbr_xpath = (f'descendant::text()[ancestor::ns:{localname}]/'
                                    f'parent::*')

        return self.xpath_float(first_desc_of_abbr_xpath) == 0.0

    @property
    def leiden_str(self) -> str:
        
        """
        Returns a Leiden-formatted string representation
        of the <expan> element
        """

        return leiden_str_from_children(
            self.e, 
            self.element_classes, 
            'element'
        )
    
    @property
    def normalized_form(self) -> str:
        return normalized_str_from_children(
            self.e, 
            self.element_classes, 
            'element'
        )

            
        
