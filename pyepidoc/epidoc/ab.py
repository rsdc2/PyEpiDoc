from __future__ import annotations
from typing import Optional

from copy import deepcopy
from functools import reduce
from lxml.etree import _Element # type: ignore

from ..base import Element
from .textpart import TextPart
from .token import Token
from .epidoctypes import (
    TokenCarrier, 
    AtomicTokenType, 
    CompoundTokenType, 
    SetRelation, 
)

from ..utils import update

from .constants import NS, XMLNS

class Ab(Element):

    def __init__(self, e:Optional[_Element]=None):
        if type(e) is not _Element and e is not None:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if self.tag.name != 'ab':
            raise TypeError('Element should be of type <ab>.')

    @property
    def compound_tokens(self) -> list[Element]:
        return [Element(item) for item 
            in self.get_desc(
                CompoundTokenType.values() 
            )
        ]

    def convert_words_to_names(self) -> Ab:

        """Converts all <w> to <name> if they are capitalized."""
        if len(self.tokens) >= 2:
            for token in self.tokens[1:]:
                token.convert_to_name()

        return self

    @property
    def expans(self) -> list[Element]:
        return [expan for expan in self.get_desc_elems_by_name('expan')]

    @property
    def gaps(self):
        return [Element(gap) for gap in self.get_desc('gap')]

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)

    @property
    def lbs(self) -> list[Element]:
        return self.get_desc_elems_by_name(['lb'])

    @property
    def _proto_word_strs(self) -> list[str]:

        """
        Returns as a list of strings the items that
        can be tokenized within the <ab/> element.
        """

        sequences = self._token_carrier_sequences
        token_carriers = [element for sequence in sequences for element in sequence]
        token_carriers_sorted = sorted(token_carriers)

        def _redfunc(acc:list[str], element:Element) -> list[str]:
            if element.text is None and element.tail_completer is None and element._tail_prototokens == []:
                return acc
        
            if element._join_to_next:
                if acc == []:
                    return element._prototokens

                return element._prototokens[:-1] + [element._prototokens[-1] + acc[0]]  + acc[1:]

            return element._prototokens + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    @property
    def token_elements(self) -> list[Element]:

        """
        Returns a list of Elements representing the text of the <ab/> element.
        Construct the sequence from right to left.
        Relies on 'element addition' as specified in the __add__ method of
        the Element object.
        """

        ab_prototokens = self.text.split()
        ab_tokens = [Element(Element.w_factory(word)) for word in ab_prototokens]        

        sequences = self._token_carrier_sequences
        token_carriers = [element for sequence in sequences 
            for element in sequence]
        token_carriers_sorted = ab_tokens + sorted(token_carriers)

        def _redfunc(acc:list[Element], element:Element) -> list[Element]:
            if element._join_to_next:
                if acc == []:
                    return element.token_elements

                if element.token_elements == []:
                    return acc
                    
                return element.token_elements[:-1] + (element.token_elements[-1] + acc[0])  + acc[1:]

            return element.token_elements + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    def set_ids(self) -> None:
        for wordcarrier in self.token_carriers:
            wordcarrier.set_id()

    def set_uuids(self) -> None:
        for wordcarrier in self.token_carriers:
            wordcarrier.set_uuid()

    @property
    def textparts(self) -> list[TextPart]:
        return [TextPart(part) for part in self.get_div_descendants('textpart')]

    def tokenize(self, inplace=True) -> Optional[Ab]:
        """
        Tokenizes the current node. 
        """

        tokenized_elements = []

        if self._e is None:
            return None

        if not inplace:
            _e = deepcopy(self._e)

            for element in self.token_elements:
                tokenized_elements += [deepcopy(element)]

        else:
            _e = self._e
            tokenized_elements = self.token_elements

        for child in list(_e):
            _e.remove(child)

        _e.text = ""

        for element in tokenized_elements:
            _e.append(element._e)

        for word in self.tokens:
            word.remove_whitespace()


        return Ab(_e)

    @property
    def _token_carrier_sequences(self) -> list[list[Element]]:

        """
        Returns maximal sequences of word_carriers between whitespace.
        These sequences are what are tokenized in <w/> elements etc.
        """
        
        def _get_word_carrier_sequences(
            acc:list[list[Element]], 
            acc_desc:set[Element], 
            tokenables:list[Element]
        ) -> list[list[Element]]:
            
            if tokenables == []:
                return acc

            element = tokenables[0]

            if element in acc_desc:
                return _get_word_carrier_sequences(acc, acc_desc, tokenables[1:])

            new_acc = acc + [element.next_no_spaces]

            next_no_spaces_desc = [element_.desc_elems for element_ in element.next_no_spaces] + [element.next_no_spaces]
            next_no_spaces_desc_flat = [element for descsequence in next_no_spaces_desc for element in descsequence]
            new_acc_desc = update(acc_desc, set(next_no_spaces_desc_flat))
            
            # breakpoint()
            return _get_word_carrier_sequences(new_acc, new_acc_desc, tokenables[1:])

        def _remove_subsets(
            acc:list[list[Element]], 
            sequence:list[Element]
        ) -> list[list[Element]]:
            
            if True in [SetRelation.propersubset(set(sequence), set(acc_item)) 
                for acc_item in tokencarrier_sequences]:
                
                return acc
            
            return acc + [sequence]

        tokencarrier_sequences = _get_word_carrier_sequences([], set(), self.token_carriers)
        # breakpoint()
        return reduce(_remove_subsets, tokencarrier_sequences, [])

    @property
    def token_carriers(self) -> list[Element]:

        """
        WordCarriers are XML elements that carry text fragments
        either as element-internal text, or in their tails.
        """

        
        return [element for element in self.desc_elems 
            if element.tag.name in TokenCarrier]

    @property
    def tokens(self) -> list[Token]:
        return [Token(word) for word 
            in self.get_desc(
                AtomicTokenType.values() 
            )
        ]

    @property
    def dividers(self) -> list[Element]:
        return [Element(boundary) for boundary 
            in self.get_desc('g')
        ]