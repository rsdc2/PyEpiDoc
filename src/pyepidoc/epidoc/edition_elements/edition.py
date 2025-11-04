# This file contains the Edition class
# as well as a function 'prettify' for prettifying the XML of the edition

from __future__ import annotations

from itertools import chain
from typing import Optional, Sequence, Literal, Callable
import re

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult, _Comment

from pyepidoc.xml import XmlElement
from pyepidoc.xml.utils import editionify
from pyepidoc.shared.enums import NamedEntities
from pyepidoc.analysis.utils.division import Division
from pyepidoc.shared.constants import XMLNS
from pyepidoc.shared import default_str
from pyepidoc.shared.types import Base
from pyepidoc.shared.classes import SetRelation
from pyepidoc.shared.iterables import maxone, seek, default_str
from pyepidoc.tei.metadata.change import Change

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import TEINS, XMLNS

from .. import ids
from ..edition_element import EditionElement
from .ab import Ab
from .expan import Expan
from .l import L
from .lb import Lb
from .lg import Lg
from pyepidoc.epidoc.token import Token
from pyepidoc.epidoc.representable import Representable
from .textpart import TextPart

from pyepidoc.shared.enums import (
    SpaceUnit, 
    SpaceSeparated,
    NoSpaceBefore,
    TokenCarrier, 
    AtomicTokenType, 
    AtomicNonTokenType,
    SubatomicTagType, 
    CompoundTokenType, 
    ContainerType,
    ElementsWithLocalIds,
    ElementsWithXmlIds,
    RepresentableElements
)


def prettify(
    spaceunit: str, 
    number: int, 
    edition: Edition
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

    def _get_multiplier(element: XmlElement) -> int:
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
            elements: Sequence[XmlElement]) -> Sequence[XmlElement]:
        
        """
        Returns a list containing each element that precedes another 
        element in the input sequence. 
        """

        prevs: list[XmlElement] = []

        for element in elements:
            if element.previous_sibling is not None:
                prevs += [element.previous_sibling]

        return prevs

    def get_parents_for_first_children(
            elements: Sequence[XmlElement]
            ) -> Sequence[XmlElement]:

        """
        Returns parent elements for all first children
        """

        parents: list[XmlElement] = [] 

        for element in elements:
            if element.previous_sibling is None: # Explain why only gives parents if previous sibling is None
                if element.parent is not None:
                    parents.append(element.parent)
        
        return parents

    def prettify_first_child(element: XmlElement) -> None:
        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            spaceunit * number * (element.depth + 1)
        ]
    )

    def prettify_lb(lb: XmlElement) -> None:
        first_parent = lb.get_first_parent_by_name(['lg', 'ab', 'div'])

        if first_parent is None:
            return

        lb.tail = ''.join([
            default_str(lb.tail).strip(),
            "\n",
            (spaceunit * number) * (first_parent.depth + 1)
        ])

    def prettify_prev(element: XmlElement) -> None:
        element.tail = ''.join([
            default_str(element.tail).strip(),
            "\n",
            (spaceunit * number) * element.depth
        ])

    def prettify_parent_of_lb(element: XmlElement) -> None:
        first_parent = element.get_first_parent_by_name(['lg', 'ab', 'div'])
        if first_parent is None:
            return

        element.text = ''.join([
            default_str(element.text).strip(),
            "\n",
            (spaceunit * number) * (first_parent.depth + 1)
        ])

    def prettify_closing_tags(elements: Sequence[XmlElement]) -> None:
        for element in elements:
            if element.child_elements == []:
                continue
            lastchild = element.child_elements[-1]
            lastchild.tail = ''.join([
                default_str(lastchild.tail).strip(),
                "\n",
                spaceunit * number * (_get_multiplier(element) - 1)
            ])
            
    # Do the pretty-printing
    for tag in newlinetags:
        desc_elems = edition.get_desc_tei_elems(elem_names=[tag])

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
            edition.get_desc_tei_elems(
                ['ab', 'l', 'lg' 'lb', 'div']
                )
            )
        
    return edition


class Edition(EditionElement):

    """
    Provides services for <div type="edition> elements.
    """

    def __init__(self, e:Optional[_Element | EditionElement | XmlElement]=None):
        if not isinstance(e, (_Element, EditionElement, XmlElement)) and \
            e is not None:
            
            raise TypeError(f'Input element is of type {type(e)}. It should be _Element or Element type, or None.')

        if type(e) is _Element:
            self._e = e
        elif type(e) is EditionElement:
            self._e = e.e
        elif type(e) is XmlElement:
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
            for element in self.get_desc_tei_elems(['ab'])]

    def append_ab(self, ab: Ab) -> Ab:
        """
        Append the `<ab>` after all others. This is the same
        as simply appending any element, but: checks 
        that what is being appended is an `<ab>` element, 
        and returns the new Ab.

        """
        if ab.localname != 'ab':
            raise TypeError(f'The element is not <ab>, but is <{ab.localname}>')

        self.append_node(ab)
        return self.abs[-1]

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
    def atomic_non_tokens(self) -> list[EditionElement]:
        """
        Atomic elements that are not analyzable as 'words' 
        i.e. cannot be lemmatized
        """
        return self._get_desc_atomic_non_tokens()

    @property
    def compound_tokens(self) -> list[EditionElement]:
        return [EditionElement(item) for item 
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
    def divs(self) -> list[XmlElement]:
        return self.get_desc_tei_elems(['div'])

    @property
    def edition_text(self) -> str:
        return self.text_desc
    
    def ensure_ab(self) -> Ab:
        """
        Retrieves the last <ab> element (if it exists)
        or adds an empty one if it does not
        """

        if len(self.abs) == 0:
            return self.append_empty_ab()
        
        return self.abs[-1]

    @property
    def expans(self) -> list[Expan]:
        return [Expan(e.e) for e in self.expan_elems]
    
    # def filter_elements(self, predicate: Callable[[EpiDocElement], bool]) -> list[EpiDocElement]:
    #     self.des


    @property
    def formatted_text(self) -> str:
        _text = re.sub(r'\n\s+', '\n', self.text_desc)
        return re.sub(r'(\S)·(\S)', r'\1 · \2', _text)
    
    @staticmethod
    def from_xml_str(
        xml_str: str, 
        wrap_in_ab: bool = True) -> Edition:
        
        """
        Take an XML string containing the XML content of an 
        EpiDoc edition, and return an Edition object. Automatically 
        wraps in the `<div type="edition">` element 

        :param wrap_with_ab: Wraps the content in an `<ab>` element
        """
        
        return Edition(XmlElement.from_xml_str(editionify(xml_str, wrap_in_ab=wrap_in_ab)))

    @property
    def gaps(self) -> list[EditionElement]:
        return [EditionElement(gap) 
                for gap in self.get_desc('gap')]

    def _get_desc_representable_elements(
            self, 
            items_with_atomic_ancestors: bool = False) -> list[EditionElement]:

        """
        Get the elements that should be represented in a text edition

        :param items_with_atomic_ancestors: If True, includes those items that have
        atomic ancestors

        :return: a list of EpiDocElement
        """

        desc = map(EditionElement, self.get_desc(RepresentableElements))

        if items_with_atomic_ancestors:
            return list(desc)
        
        return [item for item in desc 
                if not item.has_ancestors_by_names(RepresentableElements)]

    def _get_desc_atomic_non_tokens(
            self, 
            items_with_token_ancestors: bool = False) -> list[EditionElement]:

        """
        Get the atomic non-token descendants e.g. `<orig>`.  

        :param include_within_tokens: If True, includes those items that have
        token ancestors

        :return: a list of EpiDocElement
        """

        desc = map(EditionElement, self.get_desc(AtomicNonTokenType.values()))

        if items_with_token_ancestors:
            return list(desc)
        
        else:
            return [item for item in desc if not item.has_ancestors_by_names(AtomicTokenType.values())]

    def _get_desc_tokens(self, include_nested: bool = False) -> list[Token]:

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

    def get_text(
            self, 
            type: Literal['leiden', 'normalized', 'xml']) -> str:
        
        """
        :param type: the type of text wanted, whether
        the Leiden version or a normalized version (i.e. with all the 
        abbreviations expanded), or the raw text content of the descendant
        XML nodes
        :return: the edition text of the document
        """
        if type == 'leiden':

            leiden = ' '.join([repr.leiden_form 
                               for repr in self.representable_no_subatomic])
            
            leiden = re.sub(r'\|\s+?\|', '|', leiden)
            leiden = re.sub(r'·\s+?·', '·', leiden)
            leiden = re.sub(r'\s{2,}', ' ', leiden)
            leiden = re.sub(r'\s?\|\s?', '|', leiden)

            return leiden.replace('|', '\n').strip()
        
        elif type == 'normalized':
            normalized = ' '.join([repr.normalized_form 
                               for repr in self.representable_no_subatomic])
            return re.sub(r'\s{2,}', ' ', normalized).strip()
        
        elif type == 'xml':
            return self.text_desc_compressed_whitespace
        
    @property
    def has_local_ids(self) -> bool:
        """
        Return True if any element that can receive a local `@n` ID has one. Return False otherwise.
        """
        for elem in self.local_idable_elements:
            if elem.local_id is not None:
                return True
            
        return False
    
    @property
    def has_xml_ids(self) -> bool:
        """
        Return True if any element that can receive an `@xml:id` ID has one. Return False otherwise.
        """
        for elem in self.xml_idable_elements:
            if elem.xml_id is not None:
                return True
            
        return False

    @property
    def local_idable_elements(self) -> list[EditionElement]:
        
        """
        Get all the tokens in the edition that should 
        receive an `@n` id.
        """

        elems = self.get_desc_tei_elems(ElementsWithLocalIds.values())
        return list(map(EditionElement, elems))
    
    @property
    def xml_idable_elements(self) -> list[EditionElement]:
        
        """
        Get all the tokens in the edition that should 
        receive an `@xml:id` id.
        """

        elems = self.get_desc_tei_elems(ElementsWithXmlIds.values())
        return list(map(EditionElement, elems))

    @staticmethod
    def _insert_w_inside_tag(element: EditionElement) -> EditionElement:

        """
        Enclose contents of `element` in <w> element. If already contains
        a <w> element returns the element unchanged
        """

        child_nodes = element.child_nodes
        w = EditionElement.create_new('w')

        for node in child_nodes:
            if isinstance(node, _Element):
                EditionElement(node).tail = ''
            w.append_node(node)

        element.remove_children()

        element.append_node(w)
        return element

    def insert_ws_inside_named_entities(
            self,
            ignore_if_contains_ws: bool = True) -> Edition:

        """
        Enclose contents of <name> and <num> tags in <w> tag,
        in place. By default does nothing if already contains a <w> 
        element.
        """
        for elemname in NamedEntities.values():

            for name in self.descendant_elements_by_local_name(elemname):
                if name.contains('w') and ignore_if_contains_ws:
                    return self
                else:
                    self._insert_w_inside_tag(EditionElement(name))

        return self

    @property
    def is_empty(self) -> bool:

        """
        Return True if the edition is present but does 
        not contain any non-comment nodes
        """
        
        if self.get_attrib('supplied') == 'unsupplied':
            return True

        if self.has_only_whitespace:
            return True
        
        return all([ab.has_only_whitespace for ab in self.abs])

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)

    @property
    def lbs(self) -> list[EditionElement]:
        return list(chain(*[ab.lbs for ab in self.abs]))

    @property
    def lemmatizability(self) -> Division:
        """
        The percentage of atomic tokens that can be lemmtized
        """

        non_lemmatizable = len(self.atomic_non_tokens)
        lemmatizable = len(self.tokens_no_nested)
        total = non_lemmatizable + lemmatizable
        return Division(lemmatizable, total)

    @property
    def lgs(self) -> list[Ab]:
        
        """
        Returns all the <ab> elements in an edition 
        as a |list| of |Lg|.
        """

        return [Lg(element._e) 
            for element in self.get_desc_tei_elems(['lg'])]

    @property
    def local_ids(self) -> list[str | None]:
        return list(map(lambda e: e.local_id, self.local_idable_elements))

    @property
    def ls(self) -> list[Ab]:
        
        """
        Returns all the <ab> elements in an edition 
        as a |list| of |L|s.
        """

        return [L(element._e) 
            for element in self.get_desc_tei_elems(['l'])]

    def prettify(
            self, 
            spaceunit: str, 
            number: int
            ) -> Edition:
        """
        Prettify the edition text. Since this is within xml:space = "preserve",
        this involves ignoring this directive.
        """
        prettify(
            spaceunit=spaceunit, 
            number=number, 
            edition=self
        )
        return self
    
    @property
    def representable_no_subatomic(self) -> list[Representable]:
        """
        :return: the descendant elements carrying text that should be represented
        in a text edition (either Leiden or normalized)
        """

        return [Representable(word) 
                for word in self._get_desc_representable_elements(items_with_atomic_ancestors=False)]

    @property
    def resp(self) -> str | None:
        """
        Return the @resp attribute value for the edition
        """
        return self.get_attrib('resp')

    def set_ids(self, base: Base=52, compress: bool=True) -> None:
        """
        Put @xml:id on all elements of the edition,
        in place. There are two options, using either
        Base 52 or Base 100. Should keep any id that 
        already exist on an element.
        """

        for i, elem in enumerate(self.xml_idable_elements, 1):
            # Find out how long the element part of the ID should be
            elem_id_length = ids.elem_id_length_from_base(base)
            
            # Pad the element token ID with the correct amount for the base
            # Add 'wiggle room' digit
            elem_id = str(i).rjust(elem_id_length - 1, '0') + '0'

            # Stitch two IDs together
            id_xml = self.isic_document_id + '-' + elem_id

            # Set the ID, leave the compression to the element
            elem.set_id(
                id=id_xml, 
                base=base, 
                compress=compress
            )

    def set_missing_local_ids(self, interval: int=5) -> Edition:
        """
        Find any elements that don't have an `@n` id and insert 
        the correct one.

        Raises ValueError if there are not enough free ids between
        elements.
        """
        elements = self.local_idable_elements

        for i, element in enumerate(elements, 1):
            if element.local_id is None:
                previous_id_str = elements[i-2].local_id if i > 1 else "0"
                if previous_id_str is None:
                    raise Exception
                previous_id = int(previous_id_str)

                match seek(lambda e: e.has_local_id, elements[i-1:]):
                    case None:
                        element.local_id = str(i * interval)
                    case position_of_next_element_with_id, element_:
                        match element_.local_id:
                            case None:
                                raise Exception
                            case _:
                                next_id = int(element_.local_id)
                                this_id_float = previous_id + (next_id - previous_id) / (position_of_next_element_with_id + 1)
                                this_id = int(this_id_float)
                                if this_id == next_id or this_id == previous_id:
                                    raise ValueError("Could not generate unique ID")
                                
                                element.local_id = str(int(this_id))

        assert len(list(set(self.local_ids))) == len(self.local_ids)
        return self

    def set_local_ids(self, interval: int=5) -> Edition:

        """
        Put @n on certain elements in the edition.
        Raises an AttributeError if any of the elements
        already have an `@n` id.

        :param interval: the interval between ids, e.g. 
        with 5, it will be 5, 10, 15, 20 etc.
        """

        for i, element in enumerate(self.local_idable_elements, 1):
            if element.has_local_id:
                raise AttributeError(f'@n attribute already set '
                                     f'on element {element}.')
            val = i * interval
            element.local_id = str(val)

        return self

    @property
    def subtype(self) -> Optional[str]:
        return self.get_attrib('subtype')

    @property
    def supplied(self) -> Sequence[XmlElement]:
        return [elem for elem in self.descendant_elements 
            if elem.localname == 'supplied']

    @property
    def textparts(self) -> list[TextPart]:
        return [TextPart(part) 
                for part in self.get_div_descendants('textpart')]

    def token_by_local_id(self, local_id: str) -> Token | None:

        """
        Return the token with the specified ID. Returns None
        if not found. Raises an error if more than one token 
        is found with the same ID.
        """

        result = [token for token in self.tokens_incl_nested
                  if token.local_id == local_id]
        
        return maxone(result, None, True)

    def token_by_xml_id(self, xml_id: str) -> Token | None:

        """
        Return the token with the specified ID. Returns None
        if not found. Raises an error if more than one token 
        is found with the same ID.
        """

        result = [token for token in self.tokens_incl_nested
                  if token.xml_id == xml_id]
        
        return maxone(result, None, True)

    @property
    def tokens_incl_nested(self) -> list[Token]:
        """
        :return: the descendant tokens including
        tokens within tokens, e.g. <num> within <w> 
        e.g. in an abbreviated token IIviro for duoviro
        """

        return [Token(word) 
                for word in self._get_desc_tokens(include_nested=True)]        

    @property
    def token_g_dividers(self) -> list[EditionElement]:
        return [EditionElement(boundary) for boundary 
            in self.get_desc('g')
        ]

    @property
    def tokens_no_nested(self) -> list[Token]:
        """
        :return: the descendant tokens excluding
        tokens within tokens, e.g. <num> within <w> 
        e.g. in an abbreviated token IIviro for duoviro
        """

        return [Token(word) 
                for word in self._get_desc_tokens(include_nested=False)]


    @property
    def tokens_leiden_str(self) -> str:
        return ' '.join([token.leiden_plus_form 
                         for token in self.tokens_no_nested])

    @property
    def tokens_normalized_no_nested(self) -> list[Token]:

        """
        Returns list of tokens of the <div type="edition">.
        If the normalised form is an empty string,
        does not include the token.
        """

        return [token for token in self.tokens_no_nested]

    @property
    def tokens_normalized_no_nested_list_str(self) -> list[str]:
        return [token.normalized_form for token in self.tokens_no_nested]
    
    @property
    def tokens_normalized_no_nested_str(self) -> str:
        return ' '.join(self.tokens_normalized_no_nested_list_str)

    def tokenize(self, inplace: bool = True) -> Edition:
        if not inplace:
            edition = Edition(self.deepcopy())
        else:
            edition = self 
            
        for ab in edition.abs:
            ab.tokenize()   

        for l in edition.ls:
            l.tokenize()

        return edition

    @property
    def w_tokens(self) -> list[Token]:
        return [Token(word) for word in self.get_desc(['w'])]
    
    @property
    def xml_ids(self) -> list[str | None]:
        return list(map(lambda e: e.xml_id, self.xml_idable_elements))

