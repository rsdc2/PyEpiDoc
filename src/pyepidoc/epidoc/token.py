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
from ..utils import maxone, remove_none, head, to_lower
from ..constants import TEINS, XMLNS, A_TO_Z_SET, ROMAN_NUMERAL_CHARS
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
from .elements.lb import Lb
from .elements.num import Num
from .elements.supplied import Supplied
from .elements.surplus import Surplus
from .elements.unclear import Unclear
from .elements.w import W

from .enums import (
    CompoundTokenType, 
    AtomicTokenType,
    PUNCTUATION,
    OrigTextType,
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
    'lb': Lb,
    'num': Num,
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W
}

class Token(EpiDocElement):

    """
    Class for providing services for tokens, including
        lexical words <w>, 
        names <name> and
        numbers <num>.
    If present on the element,
        provides access to morphological and lemmatisation
        data.
    """
    
    def __str__(self) -> str:
        # raise AttributeError
        # breakpoint()
        return self.normalized_form

    @cached_property
    def ab_or_div_parents(self) -> Sequence[BaseElement]:

        """
        Returns a list of <ab> and <div> parent |Element|.
        """

        return self.get_ancestors_by_name(['ab', 'div'])

    @cached_property
    def ab_or_div_lang(self) -> Optional[str]:

        """
        Returns the language of the most immediate 
        <ab> or <div> parent where this is specified.
        If more than one are present, returns the first.
        """
        
        langs = [parent.get_attrib('lang', XMLNS) 
            for parent in self.ab_or_div_parents]
        
        filtered_langs = remove_none(langs)

        return maxone(filtered_langs, throw_if_more_than_one=False)

    @property
    def abbr(self) -> Optional[BaseElement]:
        """
        Returns the first <abbr> |Element|, if present,
        else None.
        """

        return maxone(
            lst=self.abbr_elems,
            defaultval=None,
            throw_if_more_than_one=False
        )

    @property
    def abbr_str(self) -> str:
        """
        Return all abbreviation text in the token 
        as a |str|.
        """

        return ''.join([abbr.text for abbr in self.abbr_elems])

    @property
    def case(self) -> Optional[str]:
        pos = self.pos
        return pos[7] if pos else None

    def convert_to_name(self, inplace=True) -> Token:
        """
        Converts the containing token tag, 
        e.g. <w>,
        to <name> if the element's text 
        starts with a capital.

        If inplace=False, returns a copy of the token.
        Otherwise returns the original token with the 
        change made.
        """

        if self.text_desc is None:
            return self
        
        if inplace:
            if self.text_desc == self.text_desc.capitalize() and \
                self.text_desc not in PUNCTUATION:

                self._e.tag = ns.give_ns('name', TEINS)    # type: ignore

            return self
        
        token_copy = Token(deepcopy(self._e))
        return token_copy.convert_to_name(True)

    @property
    def expans(self) -> list[Expan]:
        return [Expan(elem.e) for elem in self.expan_elems]

    @property
    def first_expan(self) -> Optional[Expan]:
        """
        Returns the first <expan> |Element|, if present,
        else None.
        The <expan> element contains the whole word text, 
        including both abbreviation and expansion.
        """

        return head(self.expans)

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
                
                if localname(last) in ['lb', 'w', 'name', 'persName']:
                    return acc
            
            return acc + [node]

        preceding = reversed([e for e in self.preceding_nodes_in_edition])
        following = [e for e in self.following_nodes_in_edition]

        preceding_upto_text: list[Node] = \
            list(reversed(reduce(get_next_non_text, preceding, list[Node]()))) # type: ignore
        following_upto_text: list[Node] = reduce(get_next_non_text, following, [])
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        return prec_text + self.leiden_form + following_text        

    @property
    def lemma(self) -> Optional[str]:
        return self.get_attrib('lemma')

    @lemma.setter
    def lemma(self, value:str):
        self.set_attrib('lemma', value)
        
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

    @property
    def number(self) -> Optional[str]:
        """
        :return: |str| or None containing the grammatical number of the token
        """

        return self.pos[2] if self.pos else None

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
    def pos(self) -> Optional[str]:
        """Returns the content of the part of speech (POS) 
        attribute of the token."""
        return self.get_attrib('pos')

    @pos.setter
    def pos(self, value:str):
        """
        Sets the part of speech (POS) attribute of the 
        token.
        """
        self.set_attrib('pos', value)

    def remove_element_internal_whitespace(self) -> _Element:
        
        """
        Remove all internal whitespace from word element, in place, 
        except for comments.
        """

        def _remove_whitespace_from_child(elem: _Element) -> _Element:

            for child in elem.getchildren():
                if not isinstance(child, _Comment):
                    if child.text is not None:
                        child.text = child.text.strip()
                    if child.tail is not None:
                        child.tail = child.tail.strip()

                if len(child.getchildren()) > 0:
                    child = _remove_whitespace_from_child(child) 

            return elem
        
        if self._e is None:
            raise TypeError("Underlying element is None")

        return _remove_whitespace_from_child(self._e)

    @property
    def tokens(self) -> list[Token]:
        """
        Return a list of tokens in the <ab> element.
        If tokens are nested, returns the outermost token,
        e.g. with a <num> element within a <w> element, 
        only the <w> is returned.
        """

        return list(map(Token, descendant_atomic_tokens(self)))

    @property
    def type(self) -> str:
        return self.tag.name