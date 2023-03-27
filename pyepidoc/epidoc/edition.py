from __future__ import annotations

from itertools import chain

from lxml.etree import _Element # type: ignore
from typing import Optional
import re

from .ab import Ab
from ..base import Element
from .token import Token
from .textpart import TextPart
from .empty import EmptyElement

from .epidoctypes import (
    SpaceUnit, 
    TokenCarrier, 
    AtomicTokenType, 
    SubatomicTagType, 
    CompoundTokenType, 
    ContainerType
)
from ..constants import (
    XMLNS, 
    SET_IDS, 
    SPACE_WORDS
)
from ..utils import default_str


def prettify(
    spaceunit:SpaceUnit, 
    number:int, 
    edition:Edition
) -> Edition:

    newlinetags = ['div', 'ab', 'lb']

    def _get_multiplier(element:Element) -> int:
        if element.tag.name in chain(
            AtomicTokenType.values(),
            CompoundTokenType.values(),
            SubatomicTagType.values()
        ): 
            return element.depth
        elif element.tag.name in ContainerType.values():
            return element.depth + 1
        raise ValueError("Cannot find multiplier for this element.")

    def _get_prevs(elements:list[Element]) -> list[Element]:
        prevs:list[Element] = []
        for element in elements:
            if not isinstance(element.previous, EmptyElement):
                prevs += [element.previous]

        return prevs

    def get_parents(elements:list[Element]) -> list[Element]:
        parents:list[Element] = [] 
        for element in elements:
            if isinstance(element.previous, EmptyElement):
                if not isinstance(element.parent, EmptyElement):
                    parents += [element.parent]
        
        return parents

    def prettify_lb(lb:Element) -> None:
        lb.tail = ''.join([
            default_str(lb.tail),
            "\n",
            (spaceunit.value * number) * (lb.get_first_parent_by_name(['ab', 'div']).depth + 1)
        ])

    def prettify_prev(element:Element) -> None:
        element.tail = ''.join([
            default_str(element.tail),
            "\n",
            (spaceunit.value * number) * element.depth
        ])

    def prettify_first_child(element:Element) -> None:
        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            spaceunit.value * number * (element.depth + 1)
        ])

    def prettify_parent_of_lb(element:Element) -> None:
        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            (spaceunit.value * number) * (element.get_first_parent_by_name(['ab', 'div']).depth + 1)
        ])

    def prettify_closing_tags(elements:list[Element]) -> None:
        for element in elements:
            if element.children == []:
                continue
            lastchild = element.children[-1]
            lastchild.tail = ''.join([
                default_str(lastchild.tail).strip(),
                "\n",
                (spaceunit.value * number) * (_get_multiplier(element) - 1)
            ])
            
    # Do the pretty printing
    for tag in newlinetags:
        desc_elems = edition.get_desc_elems_by_name(elem_names=[tag])

        if tag == 'ab':
            for ab in desc_elems:
                prettify_first_child(ab)

        prevs = _get_prevs(desc_elems)

        for prev in prevs:
            if tag == 'lb':
                prettify_lb(prev)
            else:
                prettify_prev(prev)

        parents = get_parents(desc_elems)

        for parent in parents:
            if tag == 'lb':
                prettify_parent_of_lb(parent)
            else:
                prettify_first_child(parent)

        prettify_closing_tags(edition.get_desc_elems_by_name(['ab', 'div']))
        
    return edition


class Edition(Element):

    def __init__(self, e:Optional[_Element]=None):
        if type(e) is not _Element and e is not None:
            raise TypeError('e should be _Element type or None.')

        self._e = e

        if self.tag.name != 'div':
            raise TypeError('Element should be of type <div>.')

        if self.get_attrib('type') != 'edition':
            raise TypeError('Element type attribute should be "edition".')
        
    @property
    def abs(self) -> list[Ab]:
        return [Ab(element._e) 
            for element in self.get_desc_elems_by_name(['ab'])]

    @property
    def compound_tokens(self) -> list[Element]:
        compound_tokens = []
        
        for ab in self.abs:
            compound_tokens += ab.compound_tokens

        return compound_tokens

    def convert_words_to_names(self) -> Edition:
        for ab in self.abs:
            ab.convert_words_to_names()
        
        return self

    @property
    def divs(self) -> list[Element]:
        return self.get_desc_elems_by_name(['div'])

    @property
    def gaps(self) -> list[Element]:
        gaps = []
        for ab in self.abs:
            gaps += ab.gaps

        return gaps

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)

    def prettify(self, spaceunit:SpaceUnit, number:int) -> None:
        prettify(spaceunit=spaceunit, number=number, edition=self)

    def space_words(self, override:bool=False) -> None:

        if SPACE_WORDS or override:
            for word in self.tokens:
                word.append_space()

            for compound in self.compound_tokens:
                compound.append_space()

            for boundary in self.token_dividers:
                boundary.append_space()

    @property
    def formatted_text(self) -> str:
        _text = re.sub(r'\n\s+', '\n', self.text_desc)
        return re.sub(r'(\S)·(\S)', r'\1 · \2', _text)

    def set_ids(self, override:bool=False) -> None:
        if SET_IDS or override:
            for ab in self.abs:
                ab.set_uuids()

    def set_uuids(self) -> None:
        if SET_IDS:
            for ab in self.abs:
                ab.set_uuids()

    @property
    def textparts(self) -> list[TextPart]:
        return [TextPart(part) for part in self.get_div_descendants('textpart')]

    def tokenize(self) -> Optional[Edition]:
        for ab in self.abs:
            ab.tokenize()

        return self

    @property
    def tokens(self) -> list[Token]:
        words = []
        
        for ab in self.abs:
            words += ab.tokens
        
        return words

    @property
    def token_dividers(self) -> list[Element]:
        dividers = []
        for ab in self.abs:
            dividers += ab.dividers
        
        return dividers
