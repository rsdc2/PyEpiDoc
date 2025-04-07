from __future__ import annotations

from typing import (
    Optional, 
    Sequence, 
    Union
)
from functools import cached_property, reduce
from copy import deepcopy
import re

from lxml.etree import (
    _Element, 
    _Comment, 
    _ElementUnicodeResult
)

from ..xml import Namespace as ns
from ..xml.utils import localname
from ..shared import maxone, remove_none, head, to_lower
from ..shared.constants import TEINS, XMLNS, A_TO_Z_SET, ROMAN_NUMERAL_CHARS
from ..xml.baseelement import BaseElement

from .element import EpiDocElement
from .utils import (
    leiden_str_from_children, 
    normalized_str_from_children,
    descendant_atomic_tokens
)
from .elements.abbr import Abbr
from .elements.am import Am
from .elements.choice import Choice
from .elements.del_elem import Del
from .elements.ex import Ex
from .elements.expan import Expan
from .elements.g import G
from .elements.gap import Gap
from .elements.hi import Hi
from .elements.lb import Lb
from .elements.num import Num
from .elements.orig import Orig
from .elements.supplied import Supplied
from .elements.surplus import Surplus
from .elements.unclear import Unclear
from .elements.w import W

from .enums import (
    CompoundTokenType, 
    AtomicTokenType,
    PUNCTUATION,
    NonNormalized,
    RegTextType
)

Node = Union[_Element, _ElementUnicodeResult]

elem_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'choice': Choice,
    'ex': Ex, 
    'del': Del,
    'expan': Expan,
    'g': G,
    'gap': Gap,
    'hi': Hi,
    'lb': Lb,
    'num': Num,
    'orig': Orig,
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W
}

class Representable(EpiDocElement):

    @property
    def form_normalized(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>, <surplus> and <del> elements
        """
        return self.normalized_form
    
    @property
    def leiden_form(self) -> str:
        """
        Returns the form per Leiden conventions, i.e. with
        abbreviations expanded with brackets
        """

        return leiden_str_from_children(self.e, elem_classes, 'node')

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: Node) -> str:
            ln = localname(n)

            if ln in ['g', 'lb', 'gap']:
                return elem_classes[ln](n).leiden_form
            
            return ''

        def get_next_non_text(
                acc: list[Node],
                node: Node
            ) -> list[Node]:

            if acc != []:
                last = acc[-1]

                if type(last) is _ElementUnicodeResult:
                    if str(last).strip() not in ['', '·']:
                        return acc 
                
                if localname(last) in ['lb', 'w', 'name', 'persName', 'num']:
                    return acc
            
            return acc + [node]

        preceding = reversed([e for e in self.preceding_nodes_in_ab])
        following = [e for e in self.following_nodes_in_ab]

        preceding_upto_text: list[Node] = \
            list(reversed(reduce(
                get_next_non_text, # type: ignore 
                preceding, 
                list[Node]()))) # type: ignore
        following_upto_text: list[Node] = reduce(get_next_non_text, following, [])
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        return prec_text + self.leiden_form + following_text        

    @cached_property
    def normalized_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @orig_form
        """
        
        if self.localname == 'num':
            return Num(self.e).normalized_form
        
        return normalized_str_from_children(self.e, elem_classes, 'node')
    
    @cached_property
    def orig_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @normalized_form
        """
        non_ancestors = RegTextType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self.xpath(f'descendant::text()[{ancestors_str}]')
        return self._clean_text(''.join([str(t) for t in normalized_text]))
    

    @property
    def type(self) -> str:
        return self.tag.name