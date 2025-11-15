from __future__ import annotations

from typing import (
    Optional, 
    Sequence, 
    Union
)
from functools import cached_property
from copy import deepcopy

from lxml.etree import (
    _Element, 
    _Comment, 
    _ElementUnicodeResult
)

from pyepidoc.xml import Namespace as ns
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.shared import maxone, remove_none, head
from pyepidoc.shared.namespaces import TEINS, XMLNS
from pyepidoc.shared.enums import (
    PUNCTUATION,
    RegTextType
)

from .utils import descendant_atomic_tokens
from .representable import Representable
from .edition_elements.abbr import Abbr
from .edition_elements.am import Am
from .edition_elements.choice import Choice
from .edition_elements.del_elem import Del
from .edition_elements.ex import Ex
from .edition_elements.expan import Expan
from .edition_elements.g import G
from .edition_elements.gap import Gap
from .edition_elements.hi import Hi
from .edition_elements.lb import Lb
from .edition_elements.num import Num
from .edition_elements.orig import Orig
from .edition_elements.supplied import Supplied
from .edition_elements.surplus import Surplus
from .edition_elements.unclear import Unclear
from .edition_elements.w import W


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
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W
}


class Token(Representable):

    """
    Class for providing services for tokens, including
        lexical words <w>, 
        names <name> and
        numbers <num>. These are elements with analysable linguistic information.

    If present on the element,
        provides access to morphological and lemmatisation
        data.
    """
    
    def __str__(self) -> str:
        return self.normalized_form

    @cached_property
    def ab_or_div_parents(self) -> Sequence[XmlElement]:

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
    def abbr(self) -> Optional[XmlElement]:
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

        return ''.join([(abbr.text or '') for abbr in self.abbr_elems])

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
    def lemma(self) -> Optional[str]:
        return self.get_attrib('lemma')

    @lemma.setter
    def lemma(self, value:str):
        self.set_attrib('lemma', value)

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

    @property
    def tokens(self) -> list[Token]:
        """
        Return a list of tokens in the token.
        If tokens are nested, returns the outermost token,
        e.g. with a <num> element within a <w> element, 
        only the <w> is returned.
        """

        return list(map(Token, descendant_atomic_tokens(self)))

