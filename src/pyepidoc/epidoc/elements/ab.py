from __future__ import annotations
from typing import Optional, Sequence, cast

from copy import deepcopy
from functools import reduce
from itertools import chain
from lxml.etree import _Element 

from ..element import EpiDocElement
from .textpart import TextPart
from ..token import Token
from .expan import Expan
from ..enums import (
    IdCarrier,
    TokenCarrier, 
    AtomicTokenType, 
    CompoundTokenType,
    NoSpaceBefore,
    NonNormalized
)
from pyepidoc.shared.classes import SetRelation
from ...xml import BaseElement
from ...shared import update_set_inplace, head
from ...shared.constants import XMLNS
from ...shared.types import Base

from pyepidoc.epidoc.utils import descendant_atomic_tokens


class Ab(EpiDocElement):

    """
    The Ab class provides services for interaction with 
    a documents <ab> elements.
    <ab> stands for 'anonymous block', see 
    https://epidoc.stoa.org/gl/latest/ref-ab.html:

    "<ab> (anonymous block) contains any arbitrary component-level 
    unit of text, acting as an anonymous container for 
    phrase or inter level elements analogous to, 
    but without the semantic baggage of, a paragraph." 
    (last accessed 2023-03-27)

    From the perspective of accessing / creating tokens,
    <ab> is the domain of tokens.
    The Ab class therefore carries the method for 
    actually doing the tokenization / collecting the tokens.
    Equivalent methods in the Edition and EpiDocCorpus
    classes call these methods for each <ab> contained
    within them.

    """

    def __init__(self, e: Optional[_Element | EpiDocElement | BaseElement]=None):

        if type(e) not in [_Element, EpiDocElement, BaseElement] and e is not None:
            raise TypeError('e should be _Element or Element type, or None.')

        if type(e) is _Element:
            self._e = e
        elif type(e) is EpiDocElement:
            self._e = e.e
        elif type(e) is BaseElement:
            self._e = e.e

        if self.tag.name != 'ab':
            raise TypeError('Element should be of type <ab>.')

    @property
    def compound_tokens(self) -> list[EpiDocElement]:
        return [EpiDocElement(item) for item 
            in self.get_desc(
                CompoundTokenType.values() 
            )
        ]

    def convert_ids(self, oldbase: Base, newbase: Base) -> None:
        for idcarrier in self.id_carriers:
            idcarrier.convert_id(oldbase, newbase)

    def convert_words_to_names(self) -> Ab:

        """Converts all <w> to <name> if they are capitalized."""

        for w in self.w_tokens:
            if w == self.first_token:
                continue
            w.convert_to_name()

        return self

    @property
    def expans(self) -> list[Expan]:
        return [Expan(e.e) for e in self.expan_elems]

    @property
    def first_token(self) -> Optional[Token]:
        return head(self.tokens)

    @property
    def g_dividers(self) -> list[EpiDocElement]:
        return [EpiDocElement(boundary) for boundary 
            in self.get_desc('g')
        ]

    @property
    def gaps(self):
        return [EpiDocElement(gap) for gap in self.get_desc('gap')]

    @property
    def id_carriers(self) -> list[EpiDocElement]:

        """
        id_carriers are XML elements that carry an 
        @xml:id attribute
        """
        return [EpiDocElement(element) 
                for element in self.desc_elems
                if element.tag.name in IdCarrier]

    @property
    def lang(self) -> Optional[str]:
        """
        :return: the @lang attribute from <ab>.
        If this is not present, ascends the hierarchy until 
        gets to the <div type="edition">
        node, at which point returns the <div> @lang attribute, if any.
        """
        
        def _get_lang(elem:EpiDocElement) -> Optional[str]:
            
            lang = elem.get_attrib('lang', XMLNS)
            
            if lang is None:
                if elem.parent is None:
                    return None
                
                if elem.localname == 'div' and elem.get_attrib('type') == 'edition':
                    return lang

                return _get_lang(elem.parent)
            
            return lang

        return _get_lang(self)

    @property
    def lbs(self) -> Sequence[EpiDocElement]:
        return [EpiDocElement(lb) 
                for lb in self.get_desc_tei_elems(['lb'])]

    @property
    def no_space_before(self) -> list[EpiDocElement]:
        """
        :return: a |list| of |Element|s that should not be separated by spaces.
        """

        return [EpiDocElement(item) for item 
            in self.get_desc(
                NoSpaceBefore.values() 
            )
        ]

    @property
    def _proto_word_strs(self) -> list[str]:

        """
        Returns as a list of strings the items that
        can be tokenized within the <ab/> element.
        """

        token_carriers = chain(*self._token_carrier_sequences)
        token_carriers_sorted = sorted(token_carriers)

        def _redfunc(acc:list[str], element:EpiDocElement) -> list[str]:
            if element.text is None and \
                element.tail_completer is None and \
                    element._tail_prototokens == []:
                return acc
        
            if element._join_to_next:
                if acc == []:
                    return element._prototokens

                return element._prototokens[:-1] + [element._prototokens[-1] + acc[0]]  + acc[1:]

            return element._prototokens + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    def set_ids(self, id: Optional[str], base: Base=52) -> None:
        for idcarrier in self.id_carriers:
            idcarrier.set_id(id, base)
    
    @property
    def textparts(self) -> list[TextPart]:
        return [TextPart(part) for part in self.get_div_descendants('textpart')]

    @property
    def token_carriers(self) -> list[EpiDocElement]:

        """
        WordCarriers are XML elements that carry text fragments
        either as element-internal text, or in their tails.
        """
        return [EpiDocElement(element) 
                for element in self.desc_elems
                if element.tag.name in TokenCarrier]

    @property
    def _token_carrier_sequences(self) -> list[list[EpiDocElement]]:

        """
        Returns maximal sequences of word_carriers between whitespace.
        These sequences are what are tokenized in <w/> elements etc.
        """
        
        def get_word_carrier_sequences(
            acc: list[list[EpiDocElement]], 
            acc_desc: set[EpiDocElement], 
            tokenables: list[EpiDocElement]
        ) -> list[list[EpiDocElement]]:

            if tokenables == []:
                return acc

            element = tokenables[0]

            if element in acc_desc:
                return get_word_carrier_sequences(acc, acc_desc, tokenables[1:])

            new_acc = acc + [element.next_no_spaces]

            next_no_spaces_desc = [element_.desc_elems 
                                   for element_ in element.next_no_spaces] + [element.next_no_spaces]
            next_no_spaces_desc_flat = [EpiDocElement(item) 
                                        for item in chain(*next_no_spaces_desc)]
            
            # NB this doesn't work if use 'update_set_copy'
            # TODO: work out why
            new_acc_desc = update_set_inplace(
                acc_desc, 
                set(next_no_spaces_desc_flat)
            )
        
            return get_word_carrier_sequences(
                new_acc, 
                new_acc_desc, 
                tokenables[1:]
            )

        def remove_subsets(
            acc: list[list[EpiDocElement]], 
            sequence: list[EpiDocElement]
        ) -> list[list[EpiDocElement]]:
            
            if any([SetRelation.propersubset(set(sequence), set(acc_item))
                for acc_item in tokencarrier_sequences]):
                
                return acc
            
            return acc + [sequence]

        tokencarrier_sequences = get_word_carrier_sequences(
            acc=[], 
            acc_desc=set(), 
            tokenables=self.token_carriers
        )
        
        return reduce(remove_subsets, tokencarrier_sequences, [])

    @property
    def token_elements(self) -> list[EpiDocElement]:

        """
        The function that does the tokenization.
        
        Returns a list of Elements representing the text of the <ab/> element.
        Constructs the sequence from right to left.
        Uses 'element addition', per the __add__ dunder method of
        the Element object, which specifies what happens at the boundary
        of two different element types.
        """

        # Get initial text before any child elements of the <ab>
        ab_prototokens = (self.text or '').split()  # split the string into tokens

        # Create token elements from the split string elements
        ab_tokens = [EpiDocElement(EpiDocElement.w_factory(word)) 
                     for word in ab_prototokens]        

        # Insert the tokens into the tree
        for token in reversed(ab_tokens):
            if self.e is not None and token.e is not None:
                self.e.insert(0, token.e)

        token_carriers = chain(*self._token_carrier_sequences)
        token_carriers_sorted = sorted(token_carriers)
        
        def _redfunc(
                acc:list[EpiDocElement], 
                element:EpiDocElement
                ) -> list[EpiDocElement]:
            
            if element._join_to_next:
                if acc == []:
                    return element.token_elements

                if element.token_elements == []:
                    return acc
            
                def sumfunc(
                    acc:list[EpiDocElement], 
                    elem:EpiDocElement) -> list[EpiDocElement]:

                    if acc == []:
                        return [elem]
                
                    new_first = elem + acc[0]

                    return new_first + acc[1:]

                # Don't sum the whole sequence every time
                # On multiple passes, information on bounding left 
                # and right appears to get lost
                return reduce(
                    sumfunc, 
                    reversed(element.token_elements + acc[:1]), 
                    cast(list[EpiDocElement], [])) + acc[1:]

            return element.token_elements + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    def tokenize(self, inplace=True) -> Optional[Ab]:
        """
        Tokenizes the current node. 
        """

        tokenized_elements = []

        if self._e is None:
            return None

        # Get the tokenized elements
        if not inplace:
            _e = deepcopy(self._e)

            for element in self.token_elements:
                tokenized_elements += [deepcopy(element)]

        else:
            _e = self._e
            tokenized_elements = self.token_elements

        # Remove existing children of <ab>
        for child in _e.getchildren():
            _e.remove(child)

        # Remove any text content of the <ab> node
        _e.text = ""    # type: ignore

        # Append the new tokenized children
        for element in tokenized_elements:
            if element._e is not None:
                _e.append(element._e)

        for token in self.tokens:
            token.remove_element_internal_whitespace()

        return self.__class__(_e)

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
    def tokens_list_leiden_str(self) -> list[str]:
        return [token.leiden_form for token in self.tokens]

    @property
    def tokens_list_normalized_str(self) -> list[str]:
        return [token.normalized_form for token in self.tokens]
    
    @property
    def tokens_normalized(self) -> list[Token]:

        """
        Returns list of tokens of the <ab>.
        If the normalised form is an empty string,
        does not include the token.
        """

        def parent_name_set(elem: _Element) -> set[str]:
            parent_names = [parent.localname 
                            for parent in Token(elem).ancestors_incl_self]
            return set(parent_names)
        
        return [Token(token_elem) for token_elem 
            in self.get_desc(AtomicTokenType.values())
            if Token(token_elem).form_normalized != '' and \
                parent_name_set(token_elem).intersection(NonNormalized.value_set()) == set()
        ]
    
    @property
    def tokens_str(self) -> str:
        return ' '.join(self.tokens_list_normalized_str)
    
    @property
    def w_tokens(self) -> list[Token]:
        return [Token(word) for word 
            in self.get_desc(['w'])
        ]
