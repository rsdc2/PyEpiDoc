from __future__ import annotations

from typing import Optional
from functools import cached_property
from copy import deepcopy

from lxml.etree import _Element # type: ignore

from ..base import Namespace as ns
from ..utils import maxone
from ..constants import NS, XMLNS
from ..base.element import Element

from .abbr import AbbrInfo
from .epidoctypes import (
    Morphology, 
    TokenInfo, 
    CompoundTokenType, 
    AtomicTokenType,
    TokenType
)


class Token(Element):

    """
    Class for providing services for tokens, including
        lexical words <w>, 
        names <name> and
        numbers <num>.
    If present on the element,
        provides access to morphological and lemmatisation
        data.
    """

    @cached_property
    def abdivparents(self) -> list[Element]:
        return self.get_parents_by_name(['ab', 'div'])

    @cached_property
    def abdivlang(self) -> Optional[str]:

        """
        Returns the language of the most immediate 
        <ab> or <div> parent where this is specified.
        """
        
        langs = [parent.get_attrib('lang', XMLNS) for parent in self.abdivparents 
            if parent.get_attrib('lang', XMLNS) is not None]

        return maxone(langs, suppress_more_than_one_error=True)

    @property
    def abbr_info(self) -> AbbrInfo:
        return AbbrInfo(form=str(self), abbr=self.abbr_str)

    @property
    def abbr_str(self) -> str:
        """
        Return all abbreviation text in the token 
        as a |str|.
        """

        return ''.join([abbr.text for abbr in self.abbrs])

    @property
    def abbrs(self) -> list[Element]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [abbr for abbr in self.get_desc_elems_by_name('abbr') 
            if abbr.text is not None]


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
            if self.text_desc == self.text_desc.capitalize():
                self._e.tag = ns.give_ns('name', NS)

            return self
        
        token_copy = Token(deepcopy(self._e))
        return token_copy.convert_to_name(True)

    @property
    def case(self) -> Optional[str]:
        pos = self.pos
        return pos[7] if pos else None


    @cached_property
    def form(self) -> str:
        return self._clean_text(self.text_desc)

    @property
    def hasabbr(self) -> bool:
        """
        Returns True if the token contains an 
        abbreviation, i.e. <abbr>.
        """
        
        return len(self.abbrs) > 0

    @property
    def hassupplied(self) -> bool:
        """
        Returns True if token contains a 
        <supplied> tag.
        """

        return len(self.supplied) > 0
        
    @property
    def lemma(self) -> Optional[str]:
        return self.get_attrib('lemma')

    @lemma.setter
    def lemma(self, value:str):
        self.set_attrib('lemma', value)

    @property
    def morphology(self) -> Morphology:
        return Morphology(full=self.pos)

    @property
    def number(self) -> Optional[str]:
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

    def remove_whitespace(self) -> Token:
        
        """Remove all internal whitespace from word element."""

        def _remove_whitespace_from_child(elem:_Element) -> _Element:

            for child in list(elem):
                if child.text is not None:
                    child.text = child.text.strip()
                if child.tail is not None:
                    child.tail = child.tail.strip()

            if len(list(elem)) > 0:
                return _remove_whitespace_from_child(child)

            return elem

        return _remove_whitespace_from_child(self._e)

    @property
    def supplied(self):
        return [Element(supplied) for supplied in self.get_desc('supplied')]

    @property
    def type(self) -> TokenType:
        return self.tag.name

    @property
    def word_info(self) -> TokenInfo:
        return TokenInfo(self.lemma, self.morphology)

    def __str__(self) -> str:
        if self.type in [
            AtomicTokenType.Name.value, 
            CompoundTokenType.PersName.value
        ]:
            return self.form.capitalize().strip().replace('·', '')
        
        if self.type in [TokenType.Num.value]:
            return self.form.upper().strip().replace('·', '')
        
        return self.form.lower().strip().replace('·', '')