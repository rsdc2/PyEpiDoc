# This file contains the Edition class
# as well as a function 'prettify' for prettifying the XML of the edition

from __future__ import annotations

from itertools import chain

from lxml.etree import _Element 
from typing import Optional, Sequence
import re

from pyepidoc.xml import BaseElement
from pyepidoc.shared.constants import XMLNS
from pyepidoc.shared import default_str
from pyepidoc.shared.types import Base
from pyepidoc.shared.classes import SetRelation

from .. import ids
from ..element import EpiDocElement
from .ab import Ab
from .expan import Expan
from .l import L
from .lb import Lb
from .lg import Lg
from ..token import Token
from .textpart import TextPart

from ..enums import (
    SpaceUnit, 
    SpaceSeparated,
    NoSpace,
    TokenCarrier, 
    AtomicTokenType, 
    SubatomicTagType, 
    CompoundTokenType, 
    ContainerType
)


def prettify(
    spaceunit:SpaceUnit, 
    number:int, 
    edition:Edition
) -> Edition:

    """
    <div type="edition"> elements generally set xml:space="preserve".
    Accordingly, built-in pretty-printers
    do not prettify the text.
    This function prettifies the edition text in particular such that 
    <lb> tags start new lines.

    Arguments:

    spaceunit -- sets the kind of unit, whether a tab or a space,
    to be used for indenting lines.

    number -- sets the number of spaceunit for each indentation.
    """

    newlinetags = ['div', 'ab', 'lg', 'l', 'lb']


    def _get_multiplier(element:BaseElement) -> int:
        if element.tag.name in chain(
            AtomicTokenType.values(),
            CompoundTokenType.values(),
            SubatomicTagType.values()
        ): 
            return element.depth
        elif element.tag.name in ContainerType.values():
            return element.depth + 1
        raise ValueError("Cannot find multiplier for this element.")

    def _get_prevs(elements:Sequence[BaseElement]) -> Sequence[BaseElement]:
        prevs:list[BaseElement] = []
        for element in elements:
            if element.previous_sibling is not None:
                prevs += [element.previous_sibling]

        return prevs

    def get_parents_for_first_children(elements:Sequence[BaseElement]) -> Sequence[BaseElement]:
        """
        Returns parent elements for all first children
        """

        parents:list[BaseElement] = [] 
        for element in elements:
            if element.previous_sibling is None: # Explain why only gives parents if previous sibling is None
                if element.parent is not None:
                    parents.append(element.parent)
        
        return parents

    def prettify_lb(lb:BaseElement) -> None:
        first_parent = lb.get_first_parent_by_name(['lg', 'ab', 'div'])
        if first_parent is None:
            return

        lb.tail = ''.join([
            default_str(lb.tail),
            "\n",
            (spaceunit.value * number) * (first_parent.depth + 1)
        ])

    def prettify_prev(element:BaseElement) -> None:
        element.tail = ''.join([
            default_str(element.tail),
            "\n",
            (spaceunit.value * number) * element.depth
        ])

    def prettify_first_child(element:BaseElement) -> None:
        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            spaceunit.value * number * (element.depth + 1)
        ])

    def prettify_parent_of_lb(element:BaseElement) -> None:
        first_parent = element.get_first_parent_by_name(['lg', 'ab', 'div'])
        if first_parent is None:
            return

        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            (spaceunit.value * number) * (first_parent.depth + 1)
        ])

    def prettify_closing_tags(elements:Sequence[BaseElement]) -> None:
        for element in elements:
            if element.child_elements == []:
                continue
            lastchild = element.child_elements[-1]
            lastchild.tail = ''.join([
                default_str(lastchild.tail).strip(),
                "\n",
                (spaceunit.value * number) * (_get_multiplier(element) - 1)
            ])
            
    # Do the pretty-printing
    for tag in newlinetags:
        desc_elems = edition.get_desc_elems_by_name(elem_names=[tag])

        if tag in ['ab', 'lg']:
            for ab in desc_elems:
                prettify_first_child(ab)

        prevs = _get_prevs(desc_elems)

        for prev in prevs:
            if tag == 'lb':
                prettify_lb(prev)
            else:
                prettify_prev(prev)

        parents = get_parents_for_first_children(desc_elems)

        for parent in parents:
            if tag == 'lb':
                prettify_parent_of_lb(parent)
            else:
                prettify_first_child(parent)

        prettify_closing_tags(edition.get_desc_elems_by_name(['ab', 'l', 'lg' 'lb', 'div']))
        
    return edition


class Edition(EpiDocElement):

    """
    Provides services for <div type="edition> elements.
    """

    def __init__(self, e:Optional[_Element | EpiDocElement | BaseElement]=None):
        if type(e) not in [_Element, EpiDocElement, BaseElement] and e is not None:
            raise TypeError('e should be _Element or Element type, or None.')

        if type(e) is _Element:
            self._e = e
        elif type(e) is EpiDocElement:
            self._e = e.e
        elif type(e) is BaseElement:
            self._e = e.e

        if self.tag.name != 'div':
            raise TypeError('Element should be of type <div>.')

        if self.get_attrib('type') != 'edition':
            raise TypeError('Element type attribute should be "edition".')
        
    @property
    def abs(self) -> list[Ab]:
        """
        Returns all the <ab> elements in an edition 
        as a |list| of |Ab|.
        """

        return [Ab(element._e) 
            for element in self.get_desc_elems_by_name(['ab'])]

    @property
    def compound_tokens(self) -> list[EpiDocElement]:
        return [EpiDocElement(item) for item 
            in self.get_desc(
                CompoundTokenType.values() 
            )
        ]

    def convert_ids(self, oldbase: Base, newbase: Base) -> None:

        # TODO This needs to be more general than abs
        for ab in self.abs:
            ab.convert_ids(oldbase, newbase)

    def convert_words_to_names(self) -> Edition:
        for ab in self.abs:
            ab.convert_words_to_names()
        
        return self

    @property
    def divs(self) -> list[BaseElement]:
        return self.get_desc_elems_by_name(['div'])

    @property
    def edition_text(self) -> str:
        return self.text_desc

    @property
    def expans(self) -> list[Expan]:
        return [Expan(e.e) for e in self.expan_elems]

    @property
    def formatted_text(self) -> str:
        _text = re.sub(r'\n\s+', '\n', self.text_desc)
        return re.sub(r'(\S)·(\S)', r'\1 · \2', _text)

    @property
    def gaps(self) -> list[EpiDocElement]:
        return [EpiDocElement(gap) 
                for gap in self.get_desc('gap')]

    def get_desc_tokens(self, include_nested: bool=False) -> list[Token]:
        """
        :param include_nested: if true, returns all the descendant tokens,
        including tokens within tokens; if false, ignores tokens within 
        tokens, e.g. <num> within <w> in e.g. IIviro = duoviro

        :return: the descendant tokens
        """

        desc = map(Token, self.get_desc(AtomicTokenType.values()))

        if include_nested:
            return list(desc)

        else:

            def has_not_token_ancestor(t: Token) -> bool:
                return not t.has_ancestors_by_names(
                    AtomicTokenType.values(),
                    SetRelation.intersection
                )
            

            desc = map(Token, self.get_desc(AtomicTokenType.values()))
            
            return list(filter(has_not_token_ancestor, desc))        

    @property
    def id_carriers(self) -> list[EpiDocElement]:
        return list(chain(*[ab.id_carriers 
                            for ab in self.abs]))

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)

    @property
    def lbs(self) -> list[EpiDocElement]:
        return list(chain(*[ab.lbs for ab in self.abs]))

    @property
    def lgs(self) -> list[Ab]:
        """
        Returns all the <ab> elements in an edition 
        as a |list| of |Lg|.
        """

        return [Lg(element._e) 
            for element in self.get_desc_elems_by_name(['lg'])]

    @property
    def ls(self) -> list[Ab]:
        """
        Returns all the <ab> elements in an edition 
        as a |list| of |L|s.
        """

        return [L(element._e) 
            for element in self.get_desc_elems_by_name(['l'])]

    @property
    def no_space(self) -> list[EpiDocElement]:
        """
        :return: |Element|s that should not be separated by spaces.
        """
        return [EpiDocElement(item) for item 
            in self.get_desc(
                NoSpace.values() 
            )
        ]

    def prettify(self, spaceunit:SpaceUnit, number:int) -> None:
        prettify(spaceunit=spaceunit, number=number, edition=self)

    def set_ids(self, base: Base=52, compress: bool=True) -> None:
        for i, elem in enumerate(self.text_elems, 1):
            # Find out how long the element part of the ID should be
            elem_id_length = ids.elem_id_length_from_base(base)
            
            # Pad the element token ID with the correct amount for the base
            # Add 'wiggle room' digit
            elem_id = str(i).rjust(elem_id_length - 1, '0') + '0'

            # Stitch two IDs together
            id_xml = self.id_isic + '-' + elem_id

            # Set the ID, leave the compression to the element
            elem.set_id(id_xml, base, compress)

    def space_tokens(self) -> None:

        """
        Separates tokens by spaces, as long as they should be separated by spaces
        and the following token is not among the tokens that should be separated
        from previous by a space
        """

        for elem in self.space_separated:
            elem.append_space()

    @property
    def space_separated(self) -> list[EpiDocElement]:
        """
        :return: |Element|s that should be separated by spaces
        """
        elems = [EpiDocElement(item) 
                 for item in self.get_desc(SpaceSeparated.values())]
        return [elem for elem in elems 
                if elem.next_sibling not in self.no_space]

    @property
    def subtype(self) -> Optional[str]:
        return self.get_attrib('subtype')

    @property
    def supplied(self) -> Sequence[BaseElement]:
        return [elem for elem in self.desc_elems 
            if elem.localname == 'supplied']

    @property
    def text_elems(self) -> list[EpiDocElement]:
        """
        All elements in the document responsible for carrying
        text information as part of the edition
        """
        elems = chain(*[ab.desc_elems for ab in self.abs])
        return list(map(EpiDocElement, elems))

    @property
    def textparts(self) -> list[TextPart]:
        return [TextPart(part) 
                for part in self.get_div_descendants('textpart')]

    def tokenize(self) -> Optional[Edition]:
        for ab in self.abs:
            ab.tokenize()   

        for l in self.ls:
            l.tokenize()

        return self

    @property
    def tokens_incl_nested(self) -> list[Token]:
        """
        :return: the descendant tokens including
        tokens within tokens, e.g. <num> within <w> 
        e.g. in an abbreviated token IIviro for duoviro
        """

        return [Token(word) 
                for word in self.get_desc_tokens(include_nested=False)]        

    @property
    def tokens_no_nested(self) -> list[Token]:
        """
        :return: the descendant tokens excluding
        tokens within tokens, e.g. <num> within <w> 
        e.g. in an abbreviated token IIviro for duoviro
        """

        return [Token(word) 
                for word in self.get_desc_tokens(include_nested=False)]

    @property
    def token_g_dividers(self) -> list[EpiDocElement]:
        return [EpiDocElement(boundary) for boundary 
            in self.get_desc('g')
        ]
    
    @property
    def tokens_leiden_str(self) -> str:
        return ' '.join([token.leiden_plus_form 
                         for token in self.tokens_no_nested])

    @property
    def tokens_normalized(self) -> list[Token]:

        """
        Returns list of tokens of the <div type="edition">.
        If the normalised form is an empty string,
        does not include the token.
        """

        return list(chain(*[ab.tokens_normalized 
                            for ab in self.abs]))

    @property
    def tokens_normalized_list_str(self) -> list[str]:
        return [token.normalized_form for token in self.tokens_no_nested]
    
    @property
    def tokens_normalized_str(self) -> str:
        return ' '.join(self.tokens_normalized_list_str)

    @property
    def w_tokens(self) -> list[Token]:
        return [Token(word) for word in self.get_desc(['w'])]
