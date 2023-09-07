from __future__ import annotations

from typing import Optional, Sequence
from functools import cached_property
from copy import deepcopy
import re

from lxml.etree import _Element, _Comment

from ..xml import Namespace as ns
from ..utils import maxone, remove_none, head
from ..constants import NS, XMLNS, A_TO_Z_SET
from .element import EpiDocElement
from ..xml.baseelement import BaseElement

from .expan import Expan
from .epidoc_types import (
    CompoundTokenType, 
    AtomicTokenType,
    PUNCTUATION
)


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
        stripped_form = re.sub(r'[·\,\.\;\:]', '', self.form.strip())

        if self.type in [
            AtomicTokenType.Name.value, 
            CompoundTokenType.PersName.value
        ]:
            return stripped_form.capitalize()
        
        # Capitalize Roman numerals only
        if self.local_name == 'num' and self.charset == 'latin':
            return stripped_form.upper()
        
        return stripped_form.lower()

    @cached_property
    def ab_or_div_parents(self) -> Sequence[BaseElement]:

        """
        Returns a list of <ab> and <div> parent |Element|.
        """

        return self.get_parents_by_name(['ab', 'div'])

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

        if self._e is None:
            return self
        
        if inplace:
            if self.text_desc == self.text_desc.capitalize() and self.text_desc not in PUNCTUATION:
                self._e.tag = ns.give_ns('name', NS)

            return self
        
        token_copy = Token(deepcopy(self._e))
        return token_copy.convert_to_name(True)

    @property
    def case(self) -> Optional[str]:
        pos = self.pos
        return pos[7] if pos else None

    @property
    def charset(self) -> str:
        return "latin" if set(self.form) - A_TO_Z_SET == set() else "other"

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

    @cached_property
    def form(self) -> str:
        """
        Returns the full form, including any abbreviation expansion.
        """

        return self._clean_text(self.text_desc)
        
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

        pos = self.pos
        return pos[2] if pos else None

    @property
    def pos(self) -> Optional[str]:
        """Returns the content of the part of speech (POS) 
        attribute of the token."""
        return self.get_attrib('pos')

    @pos.setter
    def pos(self, value:str):
        """Sets the part of speech (POS) attribute of the 
        token."""
        self.set_attrib('pos', value)

    def remove_element_internal_whitespace(self) -> _Element:
        
        """Remove all internal whitespace from word element, in place, except for comments."""

        def _remove_whitespace_from_child(elem:_Element) -> _Element:

            for child in list(elem):
                if not isinstance(child, _Comment):
                    if child.text is not None:
                        child.text = child.text.strip()
                    if child.tail is not None:
                        child.tail = child.tail.strip()

            if len(list(elem)) > 0:
                return _remove_whitespace_from_child(child)

            return elem
        
        if self._e is None:
            raise TypeError("Underlying element is None")

        return _remove_whitespace_from_child(self._e)

    @property
    def type(self) -> str:
        return self.tag.name

    # @property
    # def word_info(self) -> TokenInfo:
    #     return TokenInfo(self.lemma, self.morphology)

