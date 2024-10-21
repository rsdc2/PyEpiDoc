# This file contains the Edition class
# as well as a function 'prettify' for prettifying the XML of the edition

from __future__ import annotations

from itertools import chain
from typing import Optional, Sequence
import re

from lxml import etree
from lxml.etree import _Element 

from pyepidoc.xml import BaseElement
from pyepidoc.shared.constants import XMLNS
from pyepidoc.shared import default_str
from pyepidoc.shared.types import Base
from pyepidoc.shared.classes import SetRelation
from pyepidoc.shared.utils import maxone

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import (A_TO_Z_SET, 
                         TEINS, 
                         XMLNS, 
                         SubsumableRels,
                         ROMAN_NUMERAL_CHARS,
                         VALID_BASES)

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


    def _get_multiplier(element: BaseElement) -> int:
        if element.tag.name in chain(
            AtomicTokenType.values(),
            CompoundTokenType.values(),
            SubatomicTagType.values()
        ): 
            return element.depth
        elif element.tag.name in ContainerType.values():
            return element.depth + 1
        raise ValueError("Cannot find multiplier for this element.")

    def _get_previous_siblings(
            elements: Sequence[BaseElement]) -> Sequence[BaseElement]:
        
        """
        Returns a list containing each element that precedes another 
        element in the input sequence. 
        """

        prevs: list[BaseElement] = []

        for element in elements:
            if element.previous_sibling is not None:
                prevs += [element.previous_sibling]

        return prevs

    def get_parents_for_first_children(
            elements: Sequence[BaseElement]
            ) -> Sequence[BaseElement]:

        """
        Returns parent elements for all first children
        """

        parents: list[BaseElement] = [] 

        for element in elements:
            if element.previous_sibling is None: # Explain why only gives parents if previous sibling is None
                if element.parent is not None:
                    parents.append(element.parent)
        
        return parents

    def prettify_first_child(element: BaseElement) -> None:
        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            spaceunit.value * number * (element.depth + 1)
        ]
    )

    def prettify_lb(lb: BaseElement) -> None:
        first_parent = lb.get_first_parent_by_name(['lg', 'ab', 'div'])

        if first_parent is None:
            return

        lb.tail = ''.join([
            default_str(lb.tail).strip(),
            "\n",
            (spaceunit.value * number) * (first_parent.depth + 1)
        ])

    def prettify_prev(element: BaseElement) -> None:
        element.tail = ''.join([
            default_str(element.tail).strip(),
            "\n",
            (spaceunit.value * number) * element.depth
        ])

    def prettify_parent_of_lb(element: BaseElement) -> None:
        first_parent = element.get_first_parent_by_name(['lg', 'ab', 'div'])
        if first_parent is None:
            return

        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            (spaceunit.value * number) * (first_parent.depth + 1)
        ])

    def prettify_closing_tags(elements: Sequence[BaseElement]) -> None:
        for element in elements:
            if element.child_elements == []:
                continue
            lastchild = element.child_elements[-1]
            lastchild.tail = ''.join([
                default_str(lastchild.tail).strip(),
                "\n",
                spaceunit.value * number * (_get_multiplier(element) - 1)
            ])
            
    # Do the pretty-printing
    for tag in newlinetags:
        desc_elems = edition.get_desc_elems_by_name(elem_names=[tag])

        if tag in ['ab', 'lg']:
            for ab in desc_elems:
                prettify_first_child(ab)

        prevs = _get_previous_siblings(desc_elems)

        for prev in prevs:
            if tag == 'lb':
                # I.e. prettify the element immediately before the <lb>
                prettify_lb(prev) 

            else:
                prettify_prev(prev)

        parents = get_parents_for_first_children(desc_elems)

        for parent in parents:
            if tag == 'lb':
                prettify_parent_of_lb(parent)
            else:
                prettify_first_child(parent)

        prettify_closing_tags(
            edition.get_desc_elems_by_name(
                ['ab', 'l', 'lg' 'lb', 'div']
                )
            )
        
    return edition


class Edition(EpiDocElement):

    """
    Provides services for <div type="edition> elements.
    """

    def __init__(self, e:Optional[_Element | EpiDocElement | BaseElement]=None):
        if type(e) not in [_Element, EpiDocElement, BaseElement] and \
            e is not None:
            
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

    def append_empty_ab(self) -> Ab:
        
        """
        Append an empty <ab> after all elements in the 
        <div type=edition> element.
        """

        # Create internal <ab> element: TEI requires this
        # and insert it into the Edition element

        ab_elem = etree.Element(
            _tag = ns.give_ns('ab', TEINS),
            attrib = None,
            nsmap = None
        )

        self._e.append(ab_elem)
        return Ab(ab_elem)

    @property
    def compound_tokens(self) -> list[EpiDocElement]:
        return [EpiDocElement(item) for item 
            in self.get_desc(
                CompoundTokenType.values() 
            )
        ]

    def convert_ids(self, oldbase: Base, newbase: Base) -> None:

        """
        Convert full IDs between bases
        """
        
        # TODO This needs to be more general than abs
        for ab in self.abs:
            ab.convert_ids(oldbase, newbase)

    def convert_ws_to_names(self) -> Edition:
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

    def get_desc_tokens(self, include_nested: bool = False) -> list[Token]:

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

    @staticmethod
    def _insert_w_inside_tag(element: EpiDocElement) -> EpiDocElement:

        """
        Enclose contents of `element` in <w> element. If already contains
        a <w> element returns the element unchanged
        """

        desc_nodes = element.desc_nodes
        w = EpiDocElement.create('w')

        for node in desc_nodes:
            w.append_element_or_text(node)

        element.remove_children()

        element.append_element_or_text(w)
        return element

    def insert_w_inside_name_and_num(
            self,
            ignore_if_contains_ws: bool = True) -> Edition:

        """
        Enclose contents of <name> and <num> tags in <w> tag,
        in place. By default does nothing if already contains a <w> 
        element.
        """
        for elemname in ['name', 'num']:

            for name in self.desc_elems_by_local_name(elemname):
                if name.contains('w') and ignore_if_contains_ws:
                    return self
                else:
                    self._insert_w_inside_tag(EpiDocElement(name))

        return self

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
    def n_id_elements(self) -> list[EpiDocElement]:
        
        """
        Get all the tokens in the edition that should 
        receive an `@n` id.
        """

        elems = self.get_desc_elems_by_name(
            ['w', 'orig']
        )
        return list(map(EpiDocElement, elems))

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

    def prettify(self, spaceunit: SpaceUnit, number: int) -> None:
        """
        Prettify the edition text. Since this is within xml:space = "preserve",
        this involves ignoring this directive.
        """
        prettify(spaceunit=spaceunit, number=number, edition=self)

    def set_ids(self, base: Base=52, compress: bool=True) -> None:
        """
        Put @xml:id on all elements of the edition,
        in place. There are two options, using either
        Base 52 or Base 100. Should keep any id that 
        already exist on an element.
        """

        for i, elem in enumerate(self.text_elems, 1):
            # Find out how long the element part of the ID should be
            elem_id_length = ids.elem_id_length_from_base(base)
            
            # Pad the element token ID with the correct amount for the base
            # Add 'wiggle room' digit
            elem_id = str(i).rjust(elem_id_length - 1, '0') + '0'

            # Stitch two IDs together
            id_xml = self.id_isic + '-' + elem_id

            # Set the ID, leave the compression to the element
            elem.set_id(
                id=id_xml, 
                base=base, 
                compress=compress
            )

    def set_n_ids(self, interval: int = 5) -> Edition:

        """
        Put @n on certain elements in the edition

        :param interval: the interval between ids, e.g. 
        with 5, it will be 5, 10, 15, 20 etc.
        """

        for i, elem in enumerate(self.n_id_elements, 1):
            if elem.get_attrib('n') != None:
                raise AttributeError(f'@n attribute already set '
                                 'on element {elem}.')
            val = i * interval
            elem.set_attrib('n', str(val))

        return self

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

    def token_by_id(self, id: str) -> Token | None:

        """
        Return the token with the specified ID. Returns None
        if not found. Raises an error if more than one token 
        is found with the same ID.
        """

        result = [token for token in self.tokens_incl_nested
                  if token.id_xml == id]
        
        return maxone(result, None, True)

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

    def tokenize(self) -> Optional[Edition]:
        for ab in self.abs:
            ab.tokenize()   

        for l in self.ls:
            l.tokenize()

        return self

    @property
    def w_tokens(self) -> list[Token]:
        return [Token(word) for word in self.get_desc(['w'])]
    
