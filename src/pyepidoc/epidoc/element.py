from __future__ import annotations
from typing import (
    List,
    Sequence,
    Optional, 
    cast,
    overload
)
import sys
from itertools import chain

from pyepidoc.shared.classes import Showable, ExtendableSeq, SetRelation
from pyepidoc.shared import update_set_inplace
from pyepidoc.xml.baseelement import BaseElement

from copy import deepcopy
from functools import reduce, cached_property
import re

from lxml import etree 
from lxml.etree import ( 
    _Element,
    _ElementTree, 
    _Comment as C,
    _Comment,
    _ElementUnicodeResult
)

from pyepidoc.xml.namespace import Namespace as ns

from pyepidoc.shared.constants import (
    A_TO_Z_SET, 
    TEINS, 
    XMLNS, 
    SubsumableRels,
    ROMAN_NUMERAL_CHARS,
    VALID_BASES
)
from pyepidoc.shared.types import Base

from .enums import (
    whitespace, 
    AtomicTokenType, 
    CompoundTokenType, 
    AtomicNonTokenType,
    SubatomicTagType,
    AlwaysSubsumable,
    SpaceSeparated,
    NoSpaceBefore,
    TokenCarrier
)
from . import ids
from pyepidoc.shared import maxoneT, head, last, to_lower

sys.setrecursionlimit(10000)

def tokenize_subatomic_tags(subelement: _Element) -> EpiDocElement:
    """
    Check that subelement does not contain atomic tags
    If it does, tokenizer does not surround in an atomic tag
    """

    atomic_token_set = AtomicTokenType.value_set()
    atomic_non_token_set = AtomicNonTokenType.value_set()
    epidoc_elem = EpiDocElement(subelement)
    # atomic_descs = epidoc_elem.get_desc_elems_by_name(list(atomic_token_set))
    all_descs = epidoc_elem.desc_elems
    all_name_set = epidoc_elem.desc_elem_name_set

    if all_name_set.issubset(atomic_token_set) and all_name_set != set(): 
        # i.e. the only subelement is a name
        w = epidoc_elem # in which case do nothing

    elif epidoc_elem.localname == 'choice' and all_name_set.issubset({*atomic_token_set, 'orig', 'reg', 'sic', 'corr'}) \
        and len(all_descs) != 0 and not {'orig', 'reg', 'sic', 'corr'}.issuperset(all_name_set):
        # i.e. descendant elements are all in <choice> and at least one descendant has been tokenized
        w = EpiDocElement(subelement)  

    elif atomic_token_set.intersection(all_name_set) == {'num'}:
        # i.e. there is at least one subtoken that is an atomic token
        # and that element is a <num/> element
        # in which case surround with <w> token
        w = EpiDocElement.w_factory(subelements=[subelement])

    elif atomic_token_set.intersection(all_name_set) != set():
        # i.e. there is at least one subtoken that is an atomic token
        w = epidoc_elem # in which case do nothing
    
    elif all_name_set - atomic_non_token_set == set() and \
        all_name_set != set() and \
        subelement.tail in [None, '']:

        # i.e. subelements are only atomic non-tokens, with no
        # external text
        
        w = epidoc_elem

    else:
        # Surround in Atomic token tag
        w = EpiDocElement.w_factory(subelements=[subelement])

    if subelement.tail is not None and subelement.tail != '' and subelement.tail[-1] in ' ':
        w._final_space = True
    
    return w



class EpiDocElement(BaseElement, Showable):    

    _final_space: bool = False

    """
    Provides basic services for all EpiDoc elements.
    """

    @overload
    def __init__(
        self, 
        e: EpiDocElement,
        final_space: bool = False
    ):
        ...

    @overload
    def __init__(
        self, 
        e: BaseElement,
        final_space: bool = False
    ):
        ...

    @overload
    def __init__(
        self, 
        e: _Element,
        final_space: bool = False
    ):
        ...

    def __init__(
        self, 
        e: _Element | EpiDocElement | BaseElement,
        final_space: bool = False
    ):
        
        if not isinstance(e, (_Element, EpiDocElement, BaseElement)):
            error_msg = f'e should be _Element or Element type or None. Type is {type(e)}.'
            raise TypeError(error_msg)

        if isinstance(e, _Element):
            self._e = e
        elif isinstance(e, EpiDocElement):
            self._e = e.e
        elif isinstance(e, BaseElement):
            self._e = e.e

        self._final_space = final_space
        # if final_space:
        #     self._e.tail = ' '

    def __add__(self, other: Optional[EpiDocElement]) -> list[EpiDocElement]:
        """
        Handles appending |Element|s.
        """
        # Handle cases where other is None
        if other is None:
            return [self]

        if type(other) not in [EpiDocElement]:
            raise TypeError(f"Other element is of type {type(other)}.")

        if self._e is None and other._e is not None:
            return [other]
        
        if other._e is None and self._e is not None:
            return [self]

        if other._e is None and self._e is None:
            return [self]

        self_e = deepcopy(self._e)
        other_e = deepcopy(other._e)

        if self_e is None or other_e is None:
            return []

        # Handle unlike tags
        if self.tag != other.tag:
            # If right-bounded, never subsume
            # <lb break='no'> does not constitute a bound
            if self.right_bound and other.left_bound:
                return [self, other]
            
            if self._can_subsume(other):
                self_e.append(other_e)
                return [EpiDocElement(self_e, other._final_space)]

            if self._is_subsumable_by(other):
                self_e.tail = other.text    # type: ignore
                other_e.text = ''   # type: ignore
                other_e.insert(0, self_e)
                
                return [EpiDocElement(other_e)]
            
            return [self, other]

        # Handle like tags        
        if self.tag.name in AtomicTokenType.values() and other.tag.name in AtomicTokenType.values(): # Are there any tags that can merge apart from <w>?
            # No check for right bound, as assume 
            # spaces have already been taken into 
            # account in generating like adjacent tags
            
            first_child = head(other.child_elems)
            last_child = last(self.child_elems)
            text = other.text
            if last_child is not None:
                tail = last_child.tail
            else:
                tail = ''

            # Look inside other tag to see if contains 
            # an element that can be subsumed by self;
            # if so, merge tags
            if (text is None or text == '') and first_child is not None:
                if not self.right_bound or first_child.tag.name in AlwaysSubsumable:
                    if self._can_subsume(first_child):

                        for child in other_e.getchildren():
                            self_e.append(child)
                        return [EpiDocElement(self_e, other._final_space)]

            # Look inside self to see if other tag can 
            # subsume it;
            # if so, merge tags
            if (tail is None or tail == '') and last_child is not None:
                if not self.right_bound or last_child.tag.name in AlwaysSubsumable:
                    if other._can_subsume(last_child):
                        for child in other_e.getchildren():
                            self_e.append(child)
                        return [EpiDocElement(self_e, other._final_space)]
            
        return [EpiDocElement(self_e, self._final_space), EpiDocElement(other_e, other._final_space)]

    def __repr__(self):
        tail = '' if self.tail is None else self.tail
        content = ''.join([
            "'",
            self.tag.name, 
            "'",
            ": '", 
            self.text_desc_compressed_whitespace.strip(), 
            "'",
            f"{'; tail: ' if tail.strip() != '' else ''}", 
            tail.strip()]
        )

        return f"Element({content})"

    def __str__(self):
        return self.text_desc_compressed_whitespace

    @property
    def abbr_elems(self) -> Sequence[EpiDocElement]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [EpiDocElement(abbr) 
                for abbr in self.get_desc_tei_elems('abbr')]
        
    @property
    def am_elems(self) -> Sequence[EpiDocElement]:
        """
        Returns a |list| of abbreviation marker elements <am>.
        See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html,
        last accessed 2023-04-13.
        """

        return [EpiDocElement(abbr) 
                for abbr in self.get_desc_tei_elems('am')]

    def append_element_or_text(
            self, 
            item: _Element | _ElementUnicodeResult | str | BaseElement) -> EpiDocElement:

        """
        Append either element or text to an element
        """

        if isinstance(item, (_ElementUnicodeResult, str)):
            if self.last_child is None:
                if self.text is None:
                    self.text = item
                else:
                    self.text += item
        
            else:
                if self.last_child.tail is None:
                    self.last_child.tail = item
                else:
                    self.last_child.tail += item

        elif isinstance(item, BaseElement):
            self.e.append(item.e)

        elif isinstance(item, _Element):
            self.e.append(item)

        else:
            raise TypeError('Expected _Element or _ElementUnicodeResult')
        
        return self

    def append_space(self) -> EpiDocElement:
        """
        Appends a space to the element in place.
        """

        if self._e is None:
            return self

        if self._e.getnext() is None:
            return self

        if self._e.tail is None:
            self._e.tail = ' ' # type: ignore
            return self

        if set(self._e.tail) == {' '}:
            self._e.tail = ' '  # type: ignore
            return self
        
        self._e.tail = self._e.tail + ' '   # type: ignore
        return self

    def _can_subsume(self, other: EpiDocElement) -> bool:
        if type(other) is not EpiDocElement: 
            return False
        
        matches = list(filter(
            self._subsume_filterfunc(head=self, dep=other),
            SubsumableRels)
        )
            
        return len(matches) > 0

    @property
    def charset(self) -> str:
        return "latin" if set(self.form) - A_TO_Z_SET == set() \
            else "other"
    
    @property
    def child_elems(self) -> list[EpiDocElement]:
        return [EpiDocElement(child) for child in self.child_elements]
    
    def convert_id(self, oldbase: Base, newbase: Base) -> None:
        """
        Convert the element's @xml:id attribute to a different base
        """
        current_id = self.id_xml

        if current_id is None:
            return 
        
        self.id_xml = ids.convert(current_id, oldbase, newbase)

    @classmethod
    def create_new(cls, localname: str, attributes: dict[str, str] = dict()) -> EpiDocElement:
        """
        Create a new EpiDocElement in the TEI namespace with local name `localname` and `attributes`
        """

        tag = ns.give_ns(localname, TEINS)
        elem = etree.Element(
            tag, 
            {k: v for k, v in attributes.items()}, 
            None
        )
        return EpiDocElement(elem)
    
    def deepcopy(self) -> EpiDocElement:
        return EpiDocElement(deepcopy(self._e))

    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self.get_ancestors_incl_self()
            if type(parent.parent) is EpiDocElement])

    @property
    def dict_desc(self) -> dict[str, str | dict]:
        if self._e is None:
            return {'name': self.localname, 
                    'ns': self.tag.ns, 
                    'attrs': dict()}

        return {'name': self.localname, 
                'ns': self.tag.ns, 
                'attrs': self._e.attrib}

    @property
    def e(self) -> _Element:
        return self._e

    @property
    def ex_elems(self) -> Sequence[EpiDocElement]:
        """
        Return all abbreviation expansions (minus abbreviation) 
        as a |list| of |Element|.
        """

        return [EpiDocElement(ex) 
                for ex in self.get_desc_tei_elems('ex')]

    @property
    def expan_elems(self) -> Sequence[EpiDocElement]:
        """
        Return all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [EpiDocElement(expan) 
                for expan in self.get_desc_tei_elems('expan')]

    @property
    def final_tailtoken_boundary(self) -> bool:
        """
        Returns True if the final element of the tail is a whitespace,
        implying a word break at the end of the element.
        """

        if self.tail is None: 
            return False
        
        if self.localname == 'lb' and self.get_attrib('break') == 'no':
            return False
        
        if self.tail == '':
            return False
        
        if self.tag.name == "Comment":
            return False

        return self.tail[-1] in whitespace
    
    @property
    def _first_internal_protoword(self) -> str:
        if self._internal_prototokens == []:
            return ''
        return self._internal_prototokens[0]

    @property
    def first_internal_word_element(self) -> Optional[EpiDocElement]:

        internal_token_elements = self.get_internal_token_elements()
        if internal_token_elements == []:
            return None
        
        return internal_token_elements[0]

    @property
    def following_nodes_in_ab(self) -> list[_Element | _ElementUnicodeResult]:

        """
        Returns any following |_Element| or |_ElementUnicodeResult| whose
        ancestor is an ab.
        """

        return self._e.xpath(
            'following::node()[ancestor::x:ab]', 
            namespaces={"x": TEINS}
        )

    @property
    def following_nodes_in_edition(self) -> list[_Element]:

        """
        Returns any preceding or ancestor |_Element| whose
        ancestor is an edition.
        """

        return self._e.xpath(
            'following::node()[ancestor::x:div[@type="edition"]]', 
            namespaces={"x": TEINS}
        )

    @cached_property
    def form(self) -> str:
        """
        Returns the full form, including any abbreviation expansion.
        Compare @normalized_form
        """

        return self._clean_text(self.text_desc)

    @property
    def gaps(self) -> list[EpiDocElement]:
        return [EpiDocElement(gap) for gap in self.get_desc('gap')]
    
    @property
    def has_abbr(self) -> bool:
        """
        Returns True if the element contains an 
        abbreviation, i.e. <abbr>.
        """
        
        return len(self.abbr_elems) > 0
    
    @property
    def is_abbreviated(self) -> bool:
        return self.has_abbr

    def has_gap(self, reasons:list[str]=[]) -> bool:
        """
        Returns True if the document contains a <gap> element with a reason
        contained in the "reasons" attribute.
        If "reasons" is set to an empty list, 
        returns True if there are any gaps regardless of reason.
        """

        if self.gaps == []:
            return False
        
        # There must be gaps
        if reasons == []:
            return True

        for gap in self.gaps:
            doc_gap_reasons = gap.get_attrib('reason')
            if doc_gap_reasons is None:
                continue
            doc_gap_reasons_split = doc_gap_reasons.split()
            intersection = set(reasons).intersection(set(doc_gap_reasons_split))

            if len(intersection) > 0:
                return True

        return False

    @property
    def has_supplied(self) -> bool:
        """
        Returns True if token contains a 
        <supplied> tag.
        """

        return len(self.get_supplied()) > 0

    @property
    def id_internal(self) -> list[int]:

        """
        Unique computed element id based on hierarchical position in the XML document. 
        """
        
        def _recfunc(acc: list[int], element: Optional[EpiDocElement]) -> list[int]:
            if element is None:
                return acc 

            if element.e is None:
                return acc
            
            parent: _Element = element.e.getparent()

            if parent is None:
                return acc

            return _recfunc([parent.index(element.e, start=None, stop=None)] + acc, element.parent)

        return _recfunc([], self)

    @cached_property
    def id_isic(self) -> str:
        """
        Extracts the I.Sicily document ID from the 
        owner document of the element.
        These are of the form 'ISic012345'
        """
        if self._e is None:
            return ""

        xpathres = self._e.xpath(
            f'preceding::x:idno[@type="filename"]', 
            namespaces={"x": TEINS}
        ) 
        
        if type(xpathres) is not list:
            raise TypeError("XPath result is not a list.")

        if len(xpathres) > 0:
            return cast(str, xpathres[0].text)

        return ""

    @property
    def id_xml(self) -> Optional[str]:
        """
        Returns value of the xml:id attribute in the XML file.
        """
        return self.get_attrib('id', namespace=XMLNS)

    @id_xml.setter
    def id_xml(self, id_value:str) -> None:
        """
        Sets the value of the xml:id attribute in the XML file.
        """
        self.set_attrib('id', id_value, namespace=XMLNS)

    @property
    def _internal_prototokens(self) -> list[str]:

        if self.tail_completer is None:
            if self.tag.name in AtomicNonTokenType.values():
                return []
            
            return self._internal_tokens

        if self.tail_completer is not None:
            if self.tag.name in AtomicNonTokenType.values():
                return [self.tail_completer]

            return self._internal_tokens[:-1] + \
                [maxoneT(self._internal_tokens[-1:], '') + self.tail_completer]
            
        return []

    @property
    def _internal_tokens(self) -> list[str]:
        if self.text_desc is None:
            return []

        return self.text_desc.split()

    def get_internal_token_elements(self) -> list[EpiDocElement]:

        def remove_internal_extraneous_whitespace(e: _Element) -> _Element:
            """
            Removes extra whitespace from the tails of the elements children:
            means that correct formatting is applied when reformatted. 

            TODO: apply to all descendants
            """

            def remove_newlines_from_tail(child: _Element) -> _Element:
                if child.tail is None:
                    return child

                tail:str = child.tail
                child.tail = re.sub(r'[\n\s\t]+', ' ', tail)    # type: ignore
                return child

            def remove_newlines_from_text(child: _Element) -> _Element:
                if child.text is None:
                    return child

                text:str = child.text
                child.text = re.sub(r'[\n\s\t]+', ' ', text) # type: ignore
                return child

            _e = deepcopy(e)
            children:list[_Element] = [deepcopy(child) for child in e.getchildren()]
            
            for child in _e.getchildren():
                _e.remove(child)

            children_with_new_tails = map(remove_newlines_from_tail, children)    
            children_with_new_text = map(remove_newlines_from_text, children_with_new_tails)

            for child in children_with_new_text:
                _e.append(child)

            return _e      
            
        def make_internal_token(e: _Element) -> list[EpiDocElement]:

            """TODO merge with w_factory"""

            _e = deepcopy(e)
            _e.tail = self.tail_completer   # type: ignore
            _element = EpiDocElement(_e)
            if _element.e is None:
                return []

            if _element.tag.name in AtomicNonTokenType.values():
                internalprotowords = _element._internal_prototokens
                if internalprotowords == []:
                    return [EpiDocElement(_e, final_space=True)]

                if len(internalprotowords) == 1:
                    _e.tail = ''    # type: ignore
                    elems = EpiDocElement(_e) + EpiDocElement.w_factory(internalprotowords[0])

                    # Make sure there is a bound to the right if there are multiple tokens in the tail
                    if len(self.get_tail_token_elements()) > 0:
                        elems[-1]._final_space = True
                    return elems
                
                raise ValueError("More than 1 protoword.")

            elif _element.tag.name in AtomicTokenType.values():            
                return [_element] # i.e. do nothing because already a token

            elif _element.tag.name in CompoundTokenType.values():
                epidoc_elem = EpiDocElement(_element)
                internal_tokenized = epidoc_elem.get_child_tokens_for_container()
                epidoc_elem.remove_children()
                for element in internal_tokenized:
                    epidoc_elem.append_element_or_text(element)

                return [epidoc_elem]
            
            elif _element.tag.name in SubatomicTagType.values():
                return [tokenize_subatomic_tags(subelement=_e)]

            elif _element.tag.name == "Comment":
                comment = deepcopy(_element.e)
                comment.tail = ""   # type: ignore

                return [EpiDocElement(comment)]

            raise ValueError(f"Invalid _element.tag.name: {_element.tag.name}")
        
        if self._e is None:
            raise TypeError("Underlying element is None.")
        e = remove_internal_extraneous_whitespace(self._e)
        return make_internal_token(e)

    @property
    def is_edition(self) -> bool:
        """
        Returns True if the element is an edition <div>.
        """

        return self.localname == 'div' \
            and self.get_attrib('type') == 'edition'

    @property
    def _join_to_next(self) -> bool:
        return len(self.next_no_spaces) > 1

    @property
    def _join_to_prev(self) -> bool:
        prev_sibling = self.previous_sibling
        
        if prev_sibling is None:
            return False
        
        return EpiDocElement(prev_sibling)._join_to_next

    @property
    def lb_in_preceding_or_ancestor(self) -> Optional[_Element]:

        """
        Returns any preceding or |_Element| containing an
        <lb> element.
        cf. https://www.w3.org/TR/1999/REC-xpath-19991116/#axes
        last accessed 2023-04-20.
        """

        def get_preceding_lb(elem: EpiDocElement) -> list[_Element]:
            
            result = elem.xpath('preceding::*[descendant-or-self::ns:lb]')

            if result == []:
                if elem.parent is None:
                    return []

                return get_preceding_lb(elem.parent)

            return [item for item in result
                    if isinstance(item, _Element)]

        if self._e is None:
            return None

        return last(get_preceding_lb(self))

    @property
    def left_bound(self) -> bool:
        """
        Return False if self is <lb break='no'>, otherwise return True.
        First child only counted if the element has no text.
        Used for element addition in __add__ method.
        """

        if self.localname == 'lb' and self.get_attrib('break') == 'no':
            return False
        
        first_child = head(self.child_elems)
        if first_child is not None and (self.text == '' or self.text is None):
            if  first_child.localname == 'lb' and first_child.get_attrib('break') == 'no':
                return False
            
        return True
    
    @property
    def leiden_elems(self) -> Sequence[EpiDocElement]:
        """
        Return all abbreviation expansions 
        (i.e. abbreviation, expansion, supplied, gap) 
        as a |list| of |Element|.
        """

        return [EpiDocElement(expan) 
                for expan in self.get_desc_tei_elems([
                    'abbr',
                    'ex',
                    # 'expan',
                    'gap', 
                    'supplied',
                    'g'
                ])]

    @property
    def next_no_spaces(self) -> list[EpiDocElement]:

        """Returns a list of the next |Element|s not 
        separated by whitespace."""

        def no_break_next(element:EpiDocElement) -> bool:
            """Keep going if element is a linebreak with no word break"""
            next_elem = element.next_sibling

            if isinstance(next_elem, EpiDocElement):
                if next_elem.e is None:
                    return False
                if next_elem.e.tag == ns.give_ns('lb', TEINS):
                    if next_elem.e.attrib.get('break') == 'no':
                        return True
                if next_elem.tag.name == "Comment":
                    return True

            return False
                
        def next_no_spaces(acc: list[EpiDocElement], element: Optional[EpiDocElement]):
            
            if not isinstance(element, EpiDocElement): 
                return acc

            if no_break_next(element):
                return next_no_spaces(acc + [element], element.next_sibling)

            if element.final_tailtoken_boundary:
                return acc + [element]
            # breakpoint()
            return next_no_spaces(acc + [element], element.next_sibling)

        return next_no_spaces([], self)

    @property
    def next_sibling(self) -> Optional[EpiDocElement]:

        """
        Finds the next non-comment sibling |EpiDocElement|.
        """

        # TODO: put into base element layer; 
        # previously tried to do this but caused recursion error

        def _get_next(e:Optional[_Element]) -> Optional[_Element]:
            if e is None:
                return None

            _next_sib = e.getnext()

            if isinstance(_next_sib, _Element):
                return _next_sib
            
            e.getroottree()

            return None

        if self._e is None:
            return None

        _next = _get_next(self._e)
        
        if isinstance(_next, _Element):
            return EpiDocElement(_next)
        elif _next is None:
            return None

        return None

    @property
    def no_gaps(self) -> bool:
        """
        Returns True if the token contains 
        no <gap> tags.
        """
        return self.gaps == []

    @property
    def nospace_till_next_element(self) -> bool:
        return self._tail_prototokens == [] and not self.final_tailtoken_boundary

    @property
    def nonword_element(self) -> Optional[EpiDocElement]:
        if self._e is None:
            return None

        if self.tag.name in AtomicNonTokenType.values():
            _e = deepcopy(self._e)
            _e.tail = None  # type: ignore
            return EpiDocElement(_e)
        
        return None

    @property
    def nonword_elements(self) -> list[EpiDocElement]:
        if self.nonword_element is None:
            return []
        elif type(self.nonword_element) is EpiDocElement:
            return [self.nonword_element]

        return []
    
    @property
    def no_space_before(self) -> list[EpiDocElement]:
        """
        :return: |Element|s that should not be separated by spaces.
        """
        return [EpiDocElement(item) for item 
            in self.get_desc(
                NoSpaceBefore.values() 
            )
        ]

    @property
    def parent(self) -> Optional[EpiDocElement]:
        if self._e is None:
            return None
        _parent = self._e.getparent()
        if type(_parent) is _Element:    
            return EpiDocElement(_parent)
        elif _parent is None:
            return None
        else:
            raise TypeError('Parent is of incorrect type.')

    @property
    def preceding_nodes_in_ab(
        self) -> list[_Element | _ElementUnicodeResult]:

        """
        Returns any preceding |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:ab]', 
            namespaces={"x": TEINS}
        )

    @property
    def preceding_nodes_in_edition(
        self) -> list[_Element | _ElementUnicodeResult]:

        """
        Returns any preceding or ancestor |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:div[@type="edition"]]', 
            namespaces={"x": TEINS}
        )

    @property
    def preceding_or_ancestor_in_edition(self) -> list[_Element]:

        """
        Returns any preceding or ancestor |_Element| whose
        ancestor is an edition.
        """

        if self._e is None:
            return []

        return self._e.xpath(
            'preceding::*[ancestor::x:div[@type="edition"]]', 
            namespaces={"x": TEINS}
        ) + self._e.xpath(
            'ancestor::*[ancestor::x:div[@type="edition"]]', 
            namespaces={"x": TEINS}
        ) 

    @property
    def _prototokens(self) -> list[str]:
        return self._internal_prototokens + self._tail_prototokens

    def remove_element_internal_whitespace(self) -> _Element:
        
        """
        Remove all internal whitespace from word element, in place, 
        except for comments.
        """

        def _remove_whitespace(elem: _Element) -> _Element:

            for child in elem.getchildren():
                if not isinstance(child, _Comment):
                    if child.text is not None:
                        child.text = child.text.strip()
                    if child.tail is not None:
                        child.tail = child.tail.strip()

                if len(child.getchildren()) > 0:
                    child = _remove_whitespace(child) 

            if isinstance(elem.text, str): 
                elem.text = elem.text.strip() # type: ignore

            return elem
        
        if self._e is None:
            raise TypeError("Underlying element is None")

        return _remove_whitespace(self._e)

    @property
    def right_bound(self) -> bool:
        """
        Return False if self or last child is <lb break='no'>, otherwise return True.
        Last child only counted if the last child has no tail.
        Used for element addition in __add__ method.
        """

        if self.localname == 'lb' and self.get_attrib('break') == 'no':
            return False
        
        if self.localname == "Commment":
            return False

        last_child = last(self.child_elems)
        if last_child is not None and (last_child.tail == '' or last_child.tail is None):
            if  last_child.localname == 'lb' and last_child.get_attrib('break') == 'no':
                return False

        if self.e is None:
            return False
        
        return self._final_space == True or self.e.tail == ' '

    @property
    def roman_numeral_chars_only(self) -> bool:
        """
        Returns True if form contains only Roman numerical chararacters
        """

        chars = set(self.form.lower())
        return chars.issubset(set(map(to_lower, ROMAN_NUMERAL_CHARS)))

    @property
    def root(self) -> BaseElement:
        return self.get_ancestors_incl_self()[-1]

    @property
    def roottree(self) -> Optional[_ElementTree]:
        root_e = self.root.e
        if root_e is None:
            return None

        return root_e.getroottree()

    def set_attrib(
        self, 
        attribname:str, 
        value:str, 
        namespace:Optional[str]=None
        ) -> None:
        
        if self._e is None:
            return

        self._e.attrib[ns.give_ns(attribname, namespace)] = value

    def set_id(
            self, 
            id: Optional[str]=None, 
            base: Base=52, 
            compress: bool=True) -> None:
        """
        Set the @xml:id attribute of the element

        :param id: the ID to apply to the attribute; if None,
        calculates the ID based on the location in the XML file

        :param base: the base to use to calculate the ID

        :param compress: whether or not to compress the ID
        """

        if id is None:
            elem_id_length = ids.elem_id_length_from_base(base)

            # Number of preceding elements
            preceding_elem_count = str(len(self.preceding_or_ancestor_in_edition))

            # Pad the element token ID with the correct amount for the base
            # Add 'wiggle room' digit
            elem_id = preceding_elem_count.rjust(elem_id_length - 1, '0') + '0'

            # Stitch two IDs together
            id_xml = self.id_isic + '-' + elem_id

            # Compress the ID, if required
            self.id_xml = ids.compress(id_xml, base) if compress else id_xml

        else:
            if compress:
                self.id_xml = ids.compress(id, base)
            else:
                self.id_xml = id

    
    def space_tokens(self) -> None:

        """
        Separates tokens by spaces, as long as they should be separated by spaces
        and the following token is not among the tokens that should be separated
        from previous by a space
        """

        for elem in self.space_separated_elements:            
            elem.append_space()

    @property
    def space_separated_elements(self) -> list[EpiDocElement]:
        """
        :return: |Element|s that should be separated by spaces. Elements
        contained in an AtomicTokenType element, such as `<w>` will not 
        have any spaces inserted between them.
        """
        elems = [item
                 for item in map(EpiDocElement, self.get_desc(SpaceSeparated.values()))
                 if not item.has_ancestors_by_names(AtomicTokenType.values())]
        
        return [elem for elem in elems 
                if elem.next_sibling not in self.no_space_before]

    def _is_subsumable_by(self, other:EpiDocElement) -> bool:
        if type(other) is not EpiDocElement: 
            return False

        matches = list(filter(self._subsume_filterfunc(head=other, dep=self), SubsumableRels))

        return len(matches) > 0

    @staticmethod
    def _subsume_filterfunc(head: EpiDocElement, dep: EpiDocElement):

        def _filterfunc(item) -> bool:
            if item['head'] != head.dict_desc:
                return False

            if item['dep']['name'] != dep.dict_desc['name']:
                return False

            if item['dep']['ns'] != dep.dict_desc['ns']:
                return False

            issubset = set(item['dep']['attrs']).issubset(set(dep.dict_desc['attrs']))

            if issubset:
                values_match = False not in [item['dep']['attrs'][key] == dep.dict_desc['attrs'][key] 
                    for key in item['dep']['attrs'].keys()]
                
                return values_match

            return False

        return _filterfunc

    @property
    def tail_completer(self) -> Optional[str]:

        if self.tail is None:
            return None

        if whitespace.intersection(set(self.tail)):

            if self.tail[0] in whitespace:
                return None
            
            rfunc = lambda acc, char: \
                acc if whitespace.intersection(set(acc)) else acc + [char]

            return ''.join(reduce(rfunc, list(self.tail), [])).strip()

        return self.tail

    def get_supplied(self) -> list[EpiDocElement]:
        return [EpiDocElement(supplied) for supplied in self.get_desc('supplied')]

    @property
    def _tail_prototokens(self) -> list[str]:

        """
        Returns separate tokens in the element's tail text, 
        but any elements attached without a space to the element is left
        to be picked up under _internal_prototokens.
        """

        if self.tail is None:
            return []

        tailsplit = [item for item in re.split(r'[\t\n\s]', self.tail) 
            if item != '']

        if whitespace.intersection(set(self.tail)):

            if self.tail[0] in whitespace:
                return tailsplit
            elif len(tailsplit) == 0:
                return []
            elif len(tailsplit) == 1:
                return []
            else:
                return tailsplit[1:]
        else:
            return []
    
    def get_tail_token_elements(self) -> list[EpiDocElement]:

        def make_words(protoword:Optional[str]) -> EpiDocElement:
            w = EpiDocElement.w_factory(protoword)
            
            if protoword is not None and protoword[-1] in whitespace:
                w._final_space = True
            
            return w

        tail_token_elems = list(map(make_words, self._tail_prototokens))
        if tail_token_elems != []:
            if self.e is not None:
                if self.e.tail != '' and self.e.tail is not None:
                    if self.e.tail[-1] in ['\n', ' ']:
                        tail_token_elems[-1]._final_space = True
                        return tail_token_elems
            
            tail_token_elems[-1]._final_space = False
        
        return tail_token_elems
            
    @property
    def text(self) -> str:
        """
        Return the text contents of the element. Returns an empty string if there is no text
        """
        if self._e is None:
            return ''

        if self._e.text is None:
            return ''
            
        return self._e.text

    @text.setter
    def text(self, value:str):
        if self._e is None:
            return

        self._e.text = value    # type: ignore

    @property
    def tokenized_children(self) -> list[EpiDocElement]:
        """
        Returns children that are already tokenized, including Comment nodes
        """

        return [child for child in self.child_elems
            if child.localname in AtomicTokenType.values() or \
                child.tag.name == "Comment"]

    @property
    def token_carriers(self) -> list[EpiDocElement]:

        """
        WordCarriers are XML elements that carry text fragments
        either as element-internal text, or in their tails.
        """
        acc = []
        for element in self.desc_elems:
            if element.tag.name in TokenCarrier:
                epidoc_element = EpiDocElement(element)
                acc.append(epidoc_element)
        return acc

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

    def get_child_tokens_for_container(self) -> list[EpiDocElement]:

        # Get initial text before any child elements of the <ab>
        ab_prototokens = (self.text or '').split()  # split the string into tokens

        # Create token elements from the split string elements
        ab_tokens = [EpiDocElement.w_factory(word)
                    for word in ab_prototokens]        

        # Insert the tokens into the tree
        for token in reversed(ab_tokens):
            if self.e is not None and token.e is not None:
                self.e.insert(0, token.e)

        token_carriers = chain(*self._token_carrier_sequences)
        token_carriers_sorted = sorted(token_carriers)
        
        def _redfunc(acc: list[EpiDocElement], element: EpiDocElement) -> list[EpiDocElement]:
            
            if element._join_to_next:
                if acc == []:
                    return element.get_child_tokens()

                if element.get_child_tokens() == []:
                    return acc
            
                def sumfunc(
                    acc: list[EpiDocElement], 
                    elem: EpiDocElement) -> list[EpiDocElement]:

                    if acc == []:
                        return [elem]
                
                    new_first = elem + acc[0]

                    return new_first + acc[1:]

                # Don't sum the whole sequence every time
                # On multiple passes, information on bounding left 
                # and right appears to get lost
                return reduce(
                    sumfunc, 
                    reversed(element.get_child_tokens() + acc[:1]), 
                    cast(list[EpiDocElement], [])) + acc[1:]

            return element.get_child_tokens() + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    def get_child_tokens(self) -> list[EpiDocElement]:
        """
        Returns all potential child tokens.
        For use in tokenization.
        """

        if self.localname in ['ab']:
            return self.get_child_tokens_for_container()

        token_elems = self.get_internal_token_elements() + self.get_tail_token_elements()
        
        if token_elems != []:
            if self.e is not None:
                if self.e.tail != '' and self.e.tail is not None:
                    if self.e.tail[-1] in ['\n', ' ']:
                        token_elems[-1]._final_space = True
                        return token_elems
                    
            token_elems[-1]._final_space = False

        return token_elems

    def tokenize(self, inplace=True) -> EpiDocElement:
        """
        Tokenizes the current node. 
        """

        tokenized_elements = []

        # Get the tokenized elements
        if not inplace:
            _e = deepcopy(self._e)

            for element in self.get_child_tokens():
                tokenized_elements += [deepcopy(element)]

        else:
            _e = self._e
            tokenized_elements = self.get_child_tokens()

        # Remove existing children of <ab>
        for child in _e.getchildren():
            _e.remove(child)

        # Remove any text content of the <ab> node
        _e.text = ""    # type: ignore

        # Append the new tokenized children
        for element in tokenized_elements:
            if element._e is not None:
                element._e = element.remove_element_internal_whitespace()
                _e.append(element._e)

        return self.__class__(_e)

    @staticmethod
    def w_factory(
        prototoken: Optional[str]=None, 
        subelements: list[_Element]=[],
        parent: Optional[_Element]=None
    ) -> EpiDocElement:

        """
        TODO merge w_factory and make_word functions.
        """

        def append_tail_or_text(_tail: Optional[str], _parent:_Element) -> _Element:

            if _tail is not None:
                tailword_strs = _tail.split()
                tailtokens = [EpiDocElement.w_factory(prototoken=tailtoken_str) 
                    for tailtoken_str in tailword_strs]
                for tailtoken in tailtokens:
                    if tailtoken.e is not None:
                        _parent.append(tailtoken.e)

            return _parent           

        new_w: _Element
        new_g: _Element

        # Handle interpuncts
        if prototoken is not None and prototoken.strip() in ['·', '·', '❦', '∙']:
            tagname = ns.give_ns('g', ns=TEINS)
            new_g = etree.Element(tagname, nsmap=None, attrib=None)

            if prototoken: 
                new_g.text = prototoken # type: ignore
                new_g.set('ref', '#interpunct')

            for e in subelements:
                new_g.append(e)

            # Final space because result of a split operation
            g_elem = EpiDocElement(new_g, final_space=True) 

            return g_elem

        elif prototoken is None and parent is not None:
            children: list[_Element] = [deepcopy(e) 
                                       for e in parent.getchildren()] 
            new_parent: _Element = deepcopy(parent)
            
            # Remove text and children from new_parent
            for child in new_parent.getchildren():
                new_parent.remove(child)

            new_parent.text = None  # type: ignore
        
            # Handle the text content of new_parent
            new_parent = append_tail_or_text(parent.text, new_parent)

            # Handle children of new_parent
            for e in children:
                e_without_tail = deepcopy(e)
                e_without_tail.tail = None   # type: ignore
                localname = ns.remove_ns(e.tag)

                if localname == 'lb' and EpiDocElement(e).get_attrib('break') == 'no':
                    lb = e_without_tail
                    lb_tail = e.tail

                    if new_parent.getchildren() == []:
                        new_parent.append(lb)
                        new_parent = append_tail_or_text(lb_tail, new_parent)    
                    else:
                        
                        last_child = new_parent.getchildren()[-1]
                        last_child.append(lb)
                        if lb_tail is not None:
                            lb_tail_strs = lb_tail.split()
                            lb.tail = lb_tail_strs[0] # type: ignore

                            new_parent = append_tail_or_text(' '.join(lb_tail_strs[1:]), new_parent)

                elif localname in AtomicTokenType.values() + AtomicNonTokenType.values():
                    new_parent.append(e_without_tail)
                    new_parent = append_tail_or_text(e.tail, new_parent)                    

                elif localname in SubatomicTagType.values(): # e.g. <expan>, <choice>, <hi>
                    if localname in CompoundTokenType.values(): # this is intended for <hi>, which is also a compound token
                        tokenized = tokenize_subatomic_tags(e_without_tail)
                        if EpiDocElement(new_parent).children == []:
                            new_parent.append(tokenized.e)

                        elif tokenized.last_child is None:
                            new_parent.append(tokenized.e)
                        else:
                            new_e = tokenized.last_child.e 
                            first_w = cast(_Element, new_parent.getchildren()[0])
                            first_w.append(new_e)
                            first_w.getchildren()[-1].tail = e.tail        

                    else:
                        new_w = tokenize_subatomic_tags(e_without_tail).e
                        new_parent.append(new_w)
                        new_parent = append_tail_or_text(e.tail, new_parent)              
                    
                elif localname in CompoundTokenType.values(): # e.g. <persName>, <orgName>, <roleName>
                    new_w_elem = EpiDocElement.w_factory(parent=e_without_tail)
                    if new_w_elem.e is not None:
                        new_parent.append(new_w_elem.e)
                        new_parent = append_tail_or_text(e.tail, new_parent)

            return EpiDocElement(new_parent, final_space=True)
        else:
            if prototoken: 
                tagname = ns.give_ns('w', ns=TEINS)
                new_w = etree.Element(tagname, None, None)
                new_w.text = prototoken # type: ignore
            else:
                new_w = etree.Element(ns.give_ns('w', ns=TEINS), None, None)
 
            for child in subelements:
                new_w.append(child)

        return EpiDocElement(new_w, final_space=True)

