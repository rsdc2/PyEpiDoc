from __future__ import annotations
from typing import Optional, Sequence
from functools import reduce
from itertools import chain

from pyepidoc.epidoc.edition_element import TokenizableElement
from .textpart import TextPart
from pyepidoc.epidoc.token import Token
from .expan import Expan
from pyepidoc.shared.enums import (
    IdCarrier,
    AtomicTokenType, 
    CompoundTokenType,
    NoSpaceBefore,
    NonNormalized
)

from pyepidoc.xml import XmlElement
from pyepidoc.shared import head
from pyepidoc.shared.namespaces import XMLNS, TEINS
from pyepidoc.shared.types import Base
from pyepidoc.epidoc.representable import RepresentableElement
from pyepidoc.epidoc.utils import descendant_atomic_tokens

class Ab(RepresentableElement):

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

    def __init__(self, e: TokenizableElement | XmlElement):
        super().__init__(e)
        
        if self._e.tag.name != 'ab':
            raise TypeError('Element should be of type <ab>.')

    @property
    def compound_tokens(self) -> list[TokenizableElement]:
        return [TokenizableElement(item) for item 
            in self.get_desc(CompoundTokenType.values())
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
    def g_dividers(self) -> list[TokenizableElement]:
        return [TokenizableElement(boundary) for boundary 
                in self.get_desc('g')]

    @property
    def gaps(self):
        return [TokenizableElement(gap) for gap in self.get_desc('gap')]

    @property
    def id_carriers(self) -> list[TokenizableElement]:

        """
        id_carriers are XML elements that carry an 
        @xml:id attribute
        """
        return [TokenizableElement(element) 
                for element in self._e.descendant_elements
                if element.tag.name in IdCarrier]

    @property
    def lang(self) -> Optional[str]:
        """
        :return: the @lang attribute from <ab>.
        If this is not present, ascends the hierarchy until 
        gets to the <div type="edition">
        node, at which point returns the <div> @lang attribute, if any.
        """
        
        def _get_lang(elem:TokenizableElement) -> Optional[str]:
            
            lang = elem.get_attr('lang', XMLNS)
            
            if lang is None:
                if elem.parent is None:
                    return None
                
                if elem._e.localname == 'div' and elem.get_attr('type') == 'edition':
                    return lang

                return _get_lang(elem.parent)
            
            return lang

        return _get_lang(self)

    @property
    def lbs(self) -> Sequence[TokenizableElement]:
        return [TokenizableElement(lb) 
                for lb in self.get_desc(['lb'])]

    @property
    def no_space_before(self) -> list[TokenizableElement]:
        """
        :return: a |list| of |Element|s that should not be separated by spaces.
        """

        return [TokenizableElement(item) for item 
                in self.get_desc(NoSpaceBefore.values())]

    @property
    def _proto_word_strs(self) -> list[str]:

        """
        Returns as a list of strings the items that
        can be tokenized within the <ab/> element.
        """

        token_carriers = chain(*self._find_token_carrier_sequences())
        token_carriers_sorted = sorted(token_carriers)

        def _redfunc(acc:list[str], element:TokenizableElement) -> list[str]:
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

        def parent_name_set(elem: XmlElement) -> set[str]:
            parent_names = [parent.localname 
                            for parent in Token(elem)._e.get_ancestors_incl_self()]
            return set(parent_names)
        
        return [Token(token_elem) for token_elem 
            in self.get_desc(AtomicTokenType.values())
            if Token(token_elem).form_normalized != '' and \
                parent_name_set(token_elem._e).intersection(NonNormalized.value_set()) == set()
        ]
    
    @property
    def tokens_str(self) -> str:
        return ' '.join(self.tokens_list_normalized_str)
    
    @property
    def w_tokens(self) -> list[Token]:
        return [Token(word) for word 
            in self.get_desc(['w'])
        ]
