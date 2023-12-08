from __future__ import annotations

from typing import (
    Optional, 
    Sequence, 
    Union, 
    Reversible,
    Callable
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
from ..xml.utils import local_name
from ..utils import maxone, remove_none, head
from ..constants import NS, XMLNS, A_TO_Z_SET
from ..xml.baseelement import BaseElement

from .element import EpiDocElement
from .utils import (
    children_nodes_leiden_str, 
    children_elems_leiden_str
)

from .abbr import Abbr
from .ex import Ex
from .supplied import Supplied
from .am import Am

from .expan import Expan
from .epidoc_types import (
    CompoundTokenType, 
    AtomicTokenType,
    PUNCTUATION,
    TextNotIncludedType
)


Node = Union[_Element, _ElementUnicodeResult]

element_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'ex': Ex, 
    'supplied': Supplied,
    'expan': Expan
    # '#text': str
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
        stripped_form = re.sub(
            r'[·\,\.\;\:]|\s+', 
            '', 
            self.normalized_form.strip()
            ).replace('\n', '').replace('\t', '')

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

    @property
    def case(self) -> Optional[str]:
        pos = self.pos
        return pos[7] if pos else None

    @property
    def charset(self) -> str:
        return "latin" if set(self.form) - A_TO_Z_SET == set() else "other"

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

                self._e.tag = ns.give_ns('name', NS)    # type: ignore

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

    @cached_property
    def form(self) -> str:
        """
        Returns the full form, including any abbreviation expansion.
        Compare @normalized_form
        """

        return self._clean_text(self.text_desc)

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
        # expans_form = ''.join([expan.leiden for expan in self.expans])
        # if expans_form == '':
        #     return self.form
    
        # return expans_form
        return children_nodes_leiden_str(self.e, element_classes)

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: Node) -> str:
            if local_name(n) == 'g':
                return ' · '
            if local_name(n) == 'lb':
                return '|'
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
                
                if local_name(last) in ['lb', 'w', 'name', 'persName']:
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
        also excludes text from <g>, <surplus> and <del> elements.
        Compare @form
        """
        non_ancestors = TextNotIncludedType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self.xpath(f'descendant::text()[{ancestors_str}]')
        return self._clean_text(''.join([str(t) for t in normalized_text]))

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

        def _remove_whitespace_from_child(elem:_Element) -> _Element:

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
    def type(self) -> str:
        return self.tag.name