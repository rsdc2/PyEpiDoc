from __future__ import annotations
from typing import (
    Sequence,
    Optional, 
    cast,
    overload,
    override
)
from itertools import chain

from pyepidoc.shared.classes import Showable, SetRelation
from pyepidoc.shared import update_set_inplace
from pyepidoc.shared.string import to_lower
from pyepidoc.xml.xml_element import XmlElement

from copy import deepcopy
from functools import reduce, cached_property
import re

from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.xml.xml_element import XmlNode, XmlElement
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.shared.namespaces import TEINS, XMLNS
from pyepidoc.shared.constants import (
    A_TO_Z_SET, 
    SubsumableRels,
    ROMAN_NUMERAL_CHARS
)
from pyepidoc.shared.types import Base

from pyepidoc.shared.enums import (
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
from pyepidoc.shared import maxoneT, head, last

# sys.setrecursionlimit(10000)

def tokenize_subatomic_tags(subelement: XmlElement) -> TokenizableElement:
    """
    Check that subelement does not contain atomic tags
    If it does, tokenizer does not surround in an atomic tag
    """

    atomic_token_set = AtomicTokenType.value_set()
    atomic_non_token_set = AtomicNonTokenType.value_set()
    epidoc_elem = TokenizableElement(subelement)
    all_descs = epidoc_elem._e.descendant_elements
    all_name_set = epidoc_elem._e.descendant_element_name_set

    if all_name_set.issubset(atomic_token_set) and all_name_set != set(): 
        # i.e. the only subelement is a name
        w = epidoc_elem # in which case do nothing

    elif epidoc_elem._e.localname == 'choice' and all_name_set.issubset({*atomic_token_set, 'orig', 'reg', 'sic', 'corr'}) \
        and len(all_descs) != 0 and not {'orig', 'reg', 'sic', 'corr'}.issuperset(all_name_set):
        # i.e. descendant elements are all in <choice> and at least one descendant has been tokenized
        w = TokenizableElement(subelement)  

    elif atomic_token_set.intersection(all_name_set) == {'num'}:
        # i.e. there is at least one subtoken that is an atomic token
        # and that element is a <num/> element
        # in which case surround with <w> token
        w = TokenizableElement.w_factory(subelements=[subelement])

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
        w = TokenizableElement.w_factory(subelements=[subelement])

    if subelement.tail is not None and subelement.tail != '' and subelement.tail[-1] in ' ':
        w._final_space = True
    
    return w



class TokenizableElement(TeiElement, Showable):    
    """
    Provides services for EpiDoc edition elements, 
    i.e. elements that would be represented in a text edition.
    """

    _final_space: bool = False

    @overload
    def __init__(
        self, 
        e: TokenizableElement,
        final_space: bool = False
    ):
        ...

    @overload
    def __init__(
        self, 
        e: TeiElement,
        final_space: bool = False
    ):
        ...

    @overload
    def __init__(
        self, 
        e: XmlElement,
        final_space: bool = False
    ):
        ...

    def __init__(
        self, 
        e: XmlElement | TeiElement | TokenizableElement,
        final_space: bool = False
    ):
        
        if not isinstance(e, (TeiElement, XmlElement, TokenizableElement)):
            error_msg = f'e should be _Element or Element type or None. Type is {type(e)}.'
            raise TypeError(error_msg)

        elif isinstance(e, TokenizableElement):
            self._e = e._e
        elif isinstance(e, TeiElement):
            self._e = e._e
        elif isinstance(e, XmlElement):
            self._e = e


        self._final_space = final_space

    def __add__(self, other: Optional[TokenizableElement]) -> list[TokenizableElement]:
        """
        Handles appending |Element|s.
        """
        # Handle cases where other is None
        if other is None:
            return [self]

        if not isinstance(other, TokenizableElement):
            raise TypeError(f"Other element is of type {type(other)}.")
        
        self_e = self._e.deepcopy()
        other_e = other._e.deepcopy()

        # Handle unlike tags
        if self._e._e.tag != other._e._e.tag:
            # If right-bounded, never subsume
            # <lb break='no'> does not constitute a bound
            if self.right_bound and other.left_bound:
                return [self, other]
            
            if self._can_subsume(other):
                self_e.append_node(other_e)
                return [TokenizableElement(self_e, other._final_space)]

            if self._is_subsumable_by(other):
                self_e.tail = other.text   
                other_e.text = ''  
                other_e.insert(0, self_e)
                
                return [TokenizableElement(other_e)]
            
            return [self, other]

        # Handle like tags        
        if self._e.tag.name in AtomicTokenType.values() \
            and other._e.tag.name in AtomicTokenType.values(): # Are there any tags that can merge apart from <w>?
            # No check for right bound, as assume 
            # spaces have already been taken into 
            # account in generating like adjacent tags
            
            first_child = head(list(other.child_elems))
            last_child = last(list(self.child_elems))
            text = other.text
            if last_child is not None:
                tail = last_child._e.tail
            else:
                tail = ''

            # Look inside other tag to see if contains 
            # an element that can be subsumed by self;
            # if so, merge tags
            if (text is None or text == '') and first_child is not None:
                if not self.right_bound or first_child._e.tag.name in AlwaysSubsumable:
                    if self._can_subsume(first_child):

                        for child in other_e.child_elements:
                            self_e.append_node(child)
                        return [TokenizableElement(self_e, other._final_space)]

            # Look inside self to see if other tag can 
            # subsume it;
            # if so, merge tags
            if (tail is None or tail == '') and last_child is not None:
                if not self.right_bound or last_child._e.tag.name in AlwaysSubsumable:
                    if other._can_subsume(last_child):
                        for child in other_e.child_elements:
                            self_e.append_node(child)
                        return [TokenizableElement(self_e, other._final_space)]
            
        return [TokenizableElement(self_e, self._final_space), TokenizableElement(other_e, other._final_space)]

    def __lt__(self, other: TokenizableElement) -> bool:
        return self._e.__lt__(other._e)
    
    def __gt__(self, other: TokenizableElement) -> bool:
        return self._e.__gt__(other._e)

    def __hash__(self) -> int:
        return self._e.__hash__()
    
    def __eq__(self, other) -> bool:
        if not hasattr(other, '_e'):
            return False
        
        return self._e.__eq__(other._e)

    def __repr__(self):
        tail = '' if self._e.tail is None else self._e.tail
        content = ''.join([
            "'",
            self._e.tag.name, 
            "'",
            ": '", 
            self._e.text_desc_compressed_whitespace.strip(), 
            "'",
            f"{'; tail: ' if tail.strip() != '' else ''}", 
            tail.strip()]
        )

        return f"Element({content})"

    def __str__(self):
        return self._e.text_desc_compressed_whitespace

    @property
    def abbr_elems(self) -> Sequence[TokenizableElement]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [TokenizableElement(abbr) 
                for abbr in self.get_desc('abbr')]
        
    @property
    def am_elems(self) -> Sequence[TokenizableElement]:
        """
        Returns a |list| of abbreviation marker elements <am>.
        See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html,
        last accessed 2023-04-13.
        """

        return [TokenizableElement(abbr) 
                for abbr in self.get_desc('am')]

    def append_space(self) -> TokenizableElement:
        """
        Appends a space to the element in place.
        """

        if self._e.next_element is None:
            return self

        if self._e.tail is None:
            self._e.tail = ' '
            return self

        if set(self._e.tail) == {' '}:
            self._e.tail = ' '
            return self
        
        self._e.tail = self._e.tail + ' '
        return self

    def _can_subsume(self, other: TokenizableElement) -> bool:
        if type(other) is not TokenizableElement: 
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
    
    @override
    @property
    def child_elems(self) -> Sequence[TokenizableElement]:
        return [TokenizableElement(child) for child in self._e.child_elements]

    def convert_id(self, oldbase: Base, newbase: Base) -> None:
        """
        Convert the element's @xml:id attribute to a different base
        """
        current_id = self.xml_id

        if current_id is None:
            return 
        
        self.xml_id = ids.convert(current_id, oldbase, newbase)
    
    def deepcopy(self) -> TokenizableElement:
        return TokenizableElement(self._e.deepcopy())

    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self._e.get_ancestors_incl_self()
            if type(parent.parent) is TokenizableElement])

    @property
    def dict_desc(self) -> dict[str, str | dict]:
        return {'name': self._e.localname, 
                'ns': self._e.tag.ns, 
                'attrs': self._e.attrs}

    @property
    def e(self) -> XmlElement:
        return self._e

    @property
    def ex_elems(self) -> Sequence[TokenizableElement]:
        """
        Return all abbreviation expansions (minus abbreviation) 
        as a |list| of |Element|.
        """

        return [TokenizableElement(ex) 
                for ex in self.get_desc('ex')]

    @property
    def expan_elems(self) -> Sequence[TokenizableElement]:
        """
        Return all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [TokenizableElement(expan) 
                for expan in self.get_desc('expan')]

    @property
    def has_whitepace_tail(self) -> bool:
        """
        Returns True if the final element of the tail is a whitespace,
        implying a word break at the end of the element.
        """

        if self._e.tail is None: 
            return False
        
        if self._e.localname == 'lb' and self.get_attr('break') == 'no':
            return False
        
        if self._e.tail == '':
            return False
        
        if self._e.tag.name == "Comment":
            return False

        return self._e.tail[-1] in whitespace
    
    @property
    def _first_internal_protoword(self) -> str:
        if self._internal_prototokens == []:
            return ''
        return self._internal_prototokens[0]

    @property
    def first_internal_word_element(self) -> Optional[TokenizableElement]:

        internal_token_elements = self.get_internal_token_elements()
        if internal_token_elements == []:
            return None
        
        return internal_token_elements[0]

    @property
    def following_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any following Element or Text nodes whose
        ancestor is an `<ab>`.
        """

        return self._e.xpath(
            'following::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @property
    def following_nodes_in_edition(self) -> list[XmlNode]:

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

        return self._e._clean_text(self._e.text_desc)

    @property
    def gaps(self) -> list[TokenizableElement]:
        return [TokenizableElement(gap) for gap in self.get_desc('gap')]
    
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

    def has_gap(self, reasons: list[str] | None = None) -> bool:
        """
        Returns True if the document contains a <gap> element with a reason
        contained in the "reasons" attribute.
        If "reasons" is set to an empty list, 
        returns True if there are any gaps regardless of reason.
        """
        if reasons is None:
            reasons = []

        if self.gaps == []:
            return False
        
        # There must be gaps
        if reasons == []:
            return True

        for gap in self.gaps:
            doc_gap_reasons = gap.get_attr('reason')
            if doc_gap_reasons is None:
                continue
            doc_gap_reasons_split = doc_gap_reasons.split()
            intersection = set(reasons).intersection(set(doc_gap_reasons_split))

            if len(intersection) > 0:
                return True

        return False

    @property
    def has_local_id(self) -> bool:
        return self.local_id != None

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
        
        def _id_internal(acc: list[int], element: TokenizableElement | None) -> list[int]:
            if element is None:
                return acc 

            if element._e is None:
                return acc
            
            parent = element._e.parent

            if parent is None:
                return acc

            new_list = [parent.index(element._e)]
            return _id_internal(new_list + acc, element.parent)

        return _id_internal([], self)

    @cached_property
    def isic_document_id(self) -> str:
        """
        Extracts the I.Sicily document ID from the 
        owner document of the element.
        These are of the form 'ISic012345'
        """
        if self._e is None:
            return ""

        xpath_result = self._e.xpath(
            f'preceding::x:idno[@type="filename"]', 
            namespaces={"x": TEINS}
        ) 
        
        if type(xpath_result) is not list:
            raise TypeError("XPath result is not a list.")

        if len(xpath_result) > 0:
            return xpath_result[0].text or ''

        return ''

    @property
    def _internal_prototokens(self) -> list[str]:

        if self.tail_completer is None:
            if self._e.tag.name in AtomicNonTokenType.values():
                return []
            
            return self._internal_tokens

        if self.tail_completer is not None:
            if self._e.tag.name in AtomicNonTokenType.values():
                return [self.tail_completer]

            return self._internal_tokens[:-1] + \
                [maxoneT(self._internal_tokens[-1:], '') + self.tail_completer]
            
        return []

    @property
    def _internal_tokens(self) -> list[str]:
        if self._e.text_desc is None:
            return []

        return self._e.text_desc.split()

    def get_internal_token_elements(self) -> list[TokenizableElement]:

        def remove_internal_extraneous_whitespace(e: XmlElement) -> XmlElement:
            """
            Removes extra whitespace from the tails of the elements children:
            means that correct formatting is applied when reformatted. 

            TODO: apply to all descendants
            """

            def remove_newlines_from_tail(child: XmlElement) -> XmlElement:
                if child.tail is None:
                    return child

                tail = child.tail
                child.tail = re.sub(r'[\n\s\t]+', ' ', tail)    
                return child

            def remove_newlines_from_text(child: XmlElement) -> XmlElement:
                if child.text is None:
                    return child

                text = child.text
                child.text = re.sub(r'[\n\s\t]+', ' ', text) 
                return child

            e_copy = deepcopy(e)
            children = [child.deepcopy() for child in e.child_elements]
            
            e_copy.remove_child_elements()

            children_with_new_tails = [remove_newlines_from_tail(child) for child in children]    
            children_with_new_text = [remove_newlines_from_text(child) for child in  children_with_new_tails]

            for child in children_with_new_text:
                e_copy.append_node(child)

            return e_copy      
            
        def make_internal_token(e: XmlElement) -> list[TokenizableElement]:

            """TODO merge with w_factory"""

            e_copy = e.deepcopy()
            e_copy.tail = self.tail_completer
            edition_element = TokenizableElement(e_copy)

            if edition_element._e.tag.name in AtomicNonTokenType.values():
                internalprotowords = edition_element._internal_prototokens
                if internalprotowords == []:
                    return [TokenizableElement(e_copy, final_space=True)]

                if len(internalprotowords) == 1:
                    e_copy.tail = ''
                    elems = TokenizableElement(e_copy) + TokenizableElement.w_factory(internalprotowords[0])

                    # Make sure there is a bound to the right if there are multiple tokens in the tail
                    if len(self.create_tail_token_elements()) > 0:
                        elems[-1]._final_space = True
                    return elems
                
                raise ValueError("More than 1 protoword.")

            elif edition_element._e.tag.name in AtomicTokenType.values():            
                return [edition_element] # i.e. do nothing because already a token

            elif edition_element._e.tag.name in CompoundTokenType.values():
                epidoc_elem = TokenizableElement(edition_element)
                internal_tokenized = epidoc_elem.make_child_tokens_for_container()
                epidoc_elem._e.remove_children()
                for element in internal_tokenized:
                    epidoc_elem._e.append_node(element._e)

                return [epidoc_elem]
            
            elif edition_element._e.tag.name in SubatomicTagType.values():
                return [tokenize_subatomic_tags(subelement=e_copy)]

            elif edition_element._e.tag.name == 'Comment':
                comment = deepcopy(edition_element.e)
                comment.tail = '' 

                return [TokenizableElement(comment)]

            raise ValueError(f"Invalid _element.tag.name: {edition_element._e.tag.name}")
        
        e = remove_internal_extraneous_whitespace(self._e)
        return make_internal_token(e)

    @property
    def is_edition(self) -> bool:
        """
        Returns True if the element is an edition <div>.
        """

        return self._e.localname == 'div' \
            and self.get_attr('type') == 'edition'

    @property
    def _join_to_next(self) -> bool:
        return len(self._find_next_no_spaces()) > 1

    @property
    def _join_to_prev(self) -> bool:
        prev_sibling = self._e.previous_element
        
        if prev_sibling is None:
            return False
        
        return TokenizableElement(prev_sibling)._join_to_next

    @property
    def has_lb_in_preceding_or_ancestor(self) -> XmlElement | None:

        """
        Returns any preceding or |_Element| containing an
        <lb> element.
        cf. https://www.w3.org/TR/1999/REC-xpath-19991116/#axes
        last accessed 2023-04-20.
        """

        def get_preceding_lb(elem: TokenizableElement) -> list[XmlElement]:
            
            result = elem._e.xpath('preceding::*[descendant-or-self::ns:lb]')

            if result == []:
                if elem.parent is None:
                    return []

                return get_preceding_lb(elem.parent)

            return [item for item in result
                    if isinstance(item, XmlElement)]
        
        return last(get_preceding_lb(self))

    @property
    def left_bound(self) -> bool:
        """
        Return False if self is <lb break='no'>, otherwise return True.
        First child only counted if the element has no text.
        Used for element addition in __add__ method.
        """

        if self._e.localname == 'lb' and self.get_attr('break') == 'no':
            return False
        
        first_child = head(list(self.child_elems))
        if first_child is not None and (self.text == '' or self.text is None):
            if  first_child._e.localname == 'lb' and first_child.get_attr('break') == 'no':
                return False
            
        return True
    
    @property
    def leiden_elems(self) -> Sequence[TokenizableElement]:
        """
        Return all abbreviation expansions 
        (i.e. abbreviation, expansion, supplied, gap) 
        as a |list| of |Element|.
        """

        return [TokenizableElement(expan) 
                for expan in self.get_desc([
                    'abbr',
                    'ex',
                    # 'expan',
                    'gap', 
                    'supplied',
                    'g'
                ])]

    def _find_next_no_spaces(self) -> list[TokenizableElement]:

        """Returns a list of the next |Element|s not 
        separated by whitespace."""

        def no_break_next(element: TokenizableElement) -> bool:
            """Keep going if element is a linebreak with no word break"""
            next_elem = element.find_next_sibling()

            if isinstance(next_elem, TokenizableElement):
                if next_elem.e is None:
                    return False
                if next_elem._e._e.tag == ns.give_ns('lb', TEINS):
                    if next_elem._e.attrs.get('break') == 'no':
                        return True
                if next_elem._e.tag.name == 'Comment':
                    return True

            return False
                
        def next_no_spaces(acc: list[TokenizableElement], element: Optional[TokenizableElement]):
            
            if not isinstance(element, TokenizableElement): 
                return acc

            if no_break_next(element):
                return next_no_spaces(acc + [element], element.find_next_sibling())

            if element.has_whitepace_tail:
                return acc + [element]
            
            return next_no_spaces(acc + [element], element.find_next_sibling())

        return next_no_spaces([], self)

    def find_next_sibling(self) -> TokenizableElement | None:

        """
        Finds the next non-comment sibling |EpiDocElement|.
        """
        next_sibling_element = self._e.next_element
        if isinstance(next_sibling_element, XmlElement):
            return TokenizableElement(next_sibling_element)

        return None

    @property
    def local_id(self) -> str | None:
        """
        Return `@n` id
        """
        return self.get_attr('n')
    
    @local_id.setter
    def local_id(self, value: str | None) -> None:
        if value is None:
            self._e.remove_attr('n')
        else:
            self._e.set_attr('n', value)

    @property
    def no_gaps(self) -> bool:
        """
        Returns True if the token contains 
        no <gap> tags.
        """
        return self.gaps == []

    @property
    def nospace_till_next_element(self) -> bool:
        return self._tail_prototokens == [] and not self.has_whitepace_tail

    @property
    def nonword_element(self) -> Optional[TokenizableElement]:
        if self._e is None:
            return None

        if self._e.tag.name in AtomicNonTokenType.values():
            _e = self._e.deepcopy()
            _e.tail = None
            return TokenizableElement(_e)
        
        return None

    @property
    def nonword_elements(self) -> list[TokenizableElement]:
        if self.nonword_element is None:
            return []
        elif type(self.nonword_element) is TokenizableElement:
            return [self.nonword_element]

        return []
    
    @property
    def no_space_before(self) -> list[TokenizableElement]:
        """
        :return: |Element|s that should not be separated by spaces.
        """
        return [TokenizableElement(item) for item 
                in self.get_desc(NoSpaceBefore.values())]

    @property
    def parent(self) -> TokenizableElement | None:
        _parent = self._e.parent
        if _parent is not None:
            return TokenizableElement(_parent)
        elif _parent is None:
            return None

    @property
    def preceding_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any preceding |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @property
    def preceding_nodes_in_edition(
        self) -> list[XmlNode]:

        """
        Returns any preceding or ancestor |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:div[@type="edition"]]', 
            namespaces={'x': TEINS}
        )

    @property
    def preceding_or_ancestor_in_edition(self) -> list[XmlNode]:

        """
        Returns any preceding or ancestor |_Element| whose
        ancestor is an edition.
        """

        if self._e is None:
            return []

        return self._e.xpath(
            'preceding::*[ancestor::x:div[@type="edition"]]', 
            namespaces={'x': TEINS}
        ) + self._e.xpath(
            'ancestor::*[ancestor::x:div[@type="edition"]]', 
            namespaces={'x': TEINS}
        ) 

    @property
    def _prototokens(self) -> list[str]:
        return self._internal_prototokens + self._tail_prototokens

    def remove_element_internal_whitespace(self) -> XmlElement:
        
        """
        Remove all internal whitespace from word element, in place, 
        except for comments.
        """

        def _remove_whitespace(elem: XmlElement) -> XmlElement:

            for child in elem.child_elements:
                if child.text is not None:
                    child.text = child.text.strip()
                if child.tail is not None:
                    child.tail = child.tail.strip()

                if len(child.child_elements) > 0:
                    child = _remove_whitespace(child) 
            
            if elem.text is None:
                return elem
            elem.text = elem.text.strip()
            return elem

        return _remove_whitespace(self._e)

    @property
    def right_bound(self) -> bool:
        """
        Return False if self or last child is <lb break='no'>, otherwise return True.
        Last child only counted if the last child has no tail.
        Used for element addition in __add__ method.
        """

        if self._e.localname == 'lb' and self.get_attr('break') == 'no':
            return False
        
        if self._e.localname == 'Comment':
            return False

        last_child = last(list(self.child_elems))
        if last_child is not None and (last_child._e.tail == '' or last_child._e.tail is None):
            if  last_child._e.localname == 'lb' and last_child._e.get_attr('break') == 'no':
                return False

        if self._e._e is None:
            return False
        
        return self._final_space == True or self._e.tail == ' '

    @property
    def roman_numeral_chars_only(self) -> bool:
        """
        Returns True if form contains only Roman numerical chararacters
        """

        chars = set(self.form.lower())
        return chars.issubset(set(map(to_lower, ROMAN_NUMERAL_CHARS)))

    @property
    def root(self) -> XmlElement:
        return self._e.get_ancestors_incl_self()[-1]

    def set_attr(
        self, 
        attribname: str, 
        value: str | None, 
        namespace: Optional[str]=None) -> None:
        
        self._e.set_attr(attribname, value, namespace)

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
        if self.xml_id is not None:
            raise ValueError('@xml:id attribute already set')

        if id is None:
            elem_id_length = ids.elem_id_length_from_base(base)

            # Number of preceding elements
            preceding_elem_count = str(len(self.preceding_or_ancestor_in_edition))

            # Pad the element token ID with the correct amount for the base
            # Add 'wiggle room' digit
            elem_id = preceding_elem_count.rjust(elem_id_length - 1, '0') + '0'

            # Stitch two IDs together
            id_xml = self.isic_document_id + '-' + elem_id

            # Compress the ID, if required
            self.xml_id = ids.compress(id_xml, base) if compress else id_xml

        else:
            if compress:
                self.xml_id = ids.compress(id, base)
            else:
                self.xml_id = id

    
    def space_tokens(self) -> None:

        """
        Separates tokens by spaces, as long as they should be separated by spaces
        and the following token is not among the tokens that should be separated
        from previous by a space
        """

        for elem in self.space_separated_elements:            
            elem.append_space()
        self.space_comments()

    def space_comments(self) -> None:
        for comment in self._e.descendant_comments:
            previous_element = comment.previous_element
            if previous_element is None:
                if comment.parent.text is None:
                    comment.parent.text = ' '
                else:
                    comment.parent.text += ' '
            if previous_element is not None:
                if previous_element.tail is None:
                    previous_element.tail = ' '
                else:
                    previous_element.tail += ' '

    @property
    def space_separated_elements(self) -> list[TokenizableElement]:
        """
        :return: |Element|s that should be separated by spaces. Elements
        contained in an AtomicTokenType element, such as `<w>` will not 
        have any spaces inserted between them.
        """
        elems = [item
                 for item in map(TokenizableElement, self.get_desc(SpaceSeparated.values()))
                 if not item._e.has_ancestors_by_names(AtomicTokenType.values())]
        
        return [elem for elem in elems 
                if elem.find_next_sibling() not in self.no_space_before]

    def _is_subsumable_by(self, other: TokenizableElement) -> bool:
        if type(other) is not TokenizableElement: 
            return False

        matches = list(filter(self._subsume_filterfunc(head=other, dep=self), SubsumableRels))

        return len(matches) > 0

    @staticmethod
    def _subsume_filterfunc(head: TokenizableElement, dep: TokenizableElement):

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

        if self._e.tail is None:
            return None

        if whitespace.intersection(set(self._e.tail)):

            if self._e.tail[0] in whitespace:
                return None
            
            rfunc = lambda acc, char: \
                acc if whitespace.intersection(set(acc)) else acc + [char]

            return ''.join(reduce(rfunc, list(self._e.tail), [])).strip()

        return self._e.tail

    def get_supplied(self) -> list[TokenizableElement]:
        return [TokenizableElement(supplied) for supplied in self.get_desc('supplied')]

    @property
    def _tail_prototokens(self) -> list[str]:

        """
        Returns separate tokens in the element's tail text, 
        but any elements attached without a space to the element is left
        to be picked up under _internal_prototokens.
        """

        if self._e.tail is None:
            return []

        tailsplit = [item for item in re.split(r'[\t\n\s]', self._e.tail) 
            if item != '']

        if whitespace.intersection(set(self._e.tail)):

            if self._e.tail[0] in whitespace:
                return tailsplit
            elif len(tailsplit) == 0:
                return []
            elif len(tailsplit) == 1:
                return []
            else:
                return tailsplit[1:]
        else:
            return []
    
    def create_tail_token_elements(self) -> list[TokenizableElement]:

        def make_words(protoword: Optional[str]) -> TokenizableElement:
            w = TokenizableElement.w_factory(protoword)
            
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
    def tokenized_children(self) -> list[TokenizableElement]:
        """
        Returns children that are already tokenized, including Comment nodes
        """

        return [TokenizableElement(child) for child in self.child_elems
            if child._e.localname in AtomicTokenType.values() or \
                child._e.tag.name == "Comment"]

    def find_token_carriers(self) -> list[TokenizableElement]:

        """
        WordCarriers are XML elements that carry text fragments
        either as element-internal text, or in their tails.
        """
        acc = []
        for element in self._e.descendant_elements:
            if element.tag.name in TokenCarrier:
                epidoc_element = TokenizableElement(element)
                acc.append(epidoc_element)
        return acc

    def _find_token_carrier_sequences(self) -> list[list[TokenizableElement]]:

        """
        Returns maximal sequences of word_carriers between whitespace.
        These sequences are what are tokenized in <w/> elements etc.
        """
        
        def get_word_carrier_sequences(
            acc: list[list[TokenizableElement]], 
            acc_desc: set[TokenizableElement], 
            tokenables: list[TokenizableElement]
        ) -> list[list[TokenizableElement]]:

            if tokenables == []:
                return acc

            element = tokenables[0]

            if element in acc_desc:
                return get_word_carrier_sequences(acc, acc_desc, tokenables[1:])

            new_acc = acc + [element._find_next_no_spaces()]

            next_no_spaces_desc = [e._e.descendant_elements 
                                   for e in element._find_next_no_spaces()] + [[e._e for e in element._find_next_no_spaces()]]
            next_no_spaces_desc_flat = [TokenizableElement(item) 
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
            acc: list[list[TokenizableElement]], 
            sequence: list[TokenizableElement]
        ) -> list[list[TokenizableElement]]:
            
            if any([SetRelation.propersubset(set(sequence), set(acc_item))
                for acc_item in tokencarrier_sequences]):
                
                return acc
            
            return acc + [sequence]

        tokencarrier_sequences = get_word_carrier_sequences(
            acc=[], 
            acc_desc=set(), 
            tokenables=self.find_token_carriers()
        )
        
        return reduce(remove_subsets, tokencarrier_sequences, [])

    def tokenize_initial_text_in_container(self):
        """
        Tokenize any initial text in a container in place, since 
        this will otherwise be ignored
        """
        # Get initial text before any child elements of the <ab>
        ab_prototokens = (self.text or '').split()  # split the string into tokens

        # Create token elements from the split string elements
        ab_tokens = [TokenizableElement.w_factory(word) for word in ab_prototokens]     

        # Ensure that any final space is preserved
        if self.text and self.text[-1] == ' ' and len(ab_tokens) > 0:
            ab_tokens[-1]._e.tail = ' '

        # Insert the tokens from the initial <ab> text into the tree as tokens
        # This is necessary, since otherwise the tokenization algorithm
        # won't be able to find its siblings
        for token in reversed(ab_tokens):
            if self._e is not None and token._e is not None:
                self._e.insert(0, token._e)

        # Remove the initial text element that has now been tokenized
        self.text = ''

    def make_child_tokens_for_container(self) -> list[TokenizableElement]:
        """
        Return the child tokens for the container. To do this
        it first tokenizes the initial text of the container in place.
        """
        self.tokenize_initial_text_in_container()

        token_carriers = list(chain(*self._find_token_carrier_sequences()))
        token_carriers_sorted = [TokenizableElement(elem) for elem 
                                 in sorted([token_carrier._e for token_carrier in token_carriers])]
        
        def _redfunc(acc: list[TokenizableElement], element: TokenizableElement) -> list[TokenizableElement]:
            
            if element._join_to_next:
                if acc == []:
                    return element.get_child_tokens()

                if element.get_child_tokens() == []:
                    return acc
            
                def sumfunc(
                    acc: list[TokenizableElement], 
                    elem: TokenizableElement) -> list[TokenizableElement]:

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
                    cast(list[TokenizableElement], [])) + acc[1:]

            return element.get_child_tokens() + acc

        return reduce(_redfunc, reversed(token_carriers_sorted), [])

    def get_child_tokens(self) -> list[TokenizableElement]:
        """
        Returns all potential child tokens.
        For use in tokenization.
        """

        if self._e.localname == 'ab':
            return self.make_child_tokens_for_container()

        internal_token_elements = self.get_internal_token_elements()
        tail_token_elements = self.create_tail_token_elements()

        token_elements = internal_token_elements + tail_token_elements
        
        if token_elements != []:
            if self.e is not None:
                if self.e.tail != '' and self.e.tail is not None:
                    if self.e.tail[-1] in ['\n', ' ']:
                        token_elements[-1]._final_space = True
                        return token_elements
                    
            token_elements[-1]._final_space = False

        return token_elements

    def tokenize(self, inplace=True) -> TokenizableElement:
        """
        Tokenizes the current node. 
        """

        tokenized_elements = []

        # Get the tokenized elements
        # TODO write tests for this
        if not inplace:
            _e = self._e.deepcopy()

            for element in self.get_child_tokens():
                tokenized_elements += [element.deepcopy()]

        else:
            _e = self._e
            
            # Find the tokens
            tokenized_elements = self.get_child_tokens()

        # Remove existing children of <ab>
        _e.remove_children()

        # Remove any text content of the <ab> node
        _e.text = ""    # type: ignore

        # Append the new tokenized children
        for element in tokenized_elements:
            element._e = element.remove_element_internal_whitespace()
            _e.append_node(element._e)

        return self.__class__(_e)

    @staticmethod
    def w_factory(
        prototoken: str | None = None, 
        subelements: list[XmlElement] = [],
        parent: XmlElement | None = None
    ) -> TokenizableElement:

        """
        TODO merge w_factory and make_word functions.
        """

        def append_tail_or_text(_tail: str | None, _parent: XmlElement) -> XmlElement:

            if _tail is not None:
                tailword_strs = _tail.split()
                tailtokens = [TokenizableElement.w_factory(prototoken=tailtoken_str) 
                    for tailtoken_str in tailword_strs]
                for tailtoken in tailtokens:
                    if tailtoken.e is not None:
                        _parent.append_node(tailtoken._e)

            return _parent           

        # Handle interpuncts
        if prototoken is not None and prototoken.strip() in ['·', '·', '❦', '∙']:
            g = XmlElement.create('g', TEINS)

            if prototoken: 
                g.text = prototoken
                g.set_attr('ref', '#interpunct')

            for child in subelements:
                g.append_node(child)

            # Set final_space to true because result of a split operation
            g_element = TokenizableElement(g, final_space=True) 

            return g_element

        elif prototoken is None and parent is not None:
            children = [e.deepcopy() for e in parent.child_elements] 
            parent_copy = parent.deepcopy()
            
            # Remove text and children from parent_copy
            parent_copy.remove_children()
            parent_copy.text = None  # type: ignore
        
            # Handle the text content of new_parent
            parent_copy = append_tail_or_text(parent.text, parent_copy)

            # Handle children of new_parent
            for child in children:
                e_without_tail = child.deepcopy()
                e_without_tail.tail = None   # type: ignore
                localname = child.localname

                if localname == 'lb' and TokenizableElement(child).get_attr('break') == 'no':
                    lb = e_without_tail
                    lb_tail = child.tail

                    if parent_copy.child_elements == []:
                        parent_copy.append_node(lb)
                        parent_copy = append_tail_or_text(lb_tail, parent_copy)    
                    else:
                        
                        last_child = parent_copy.child_elements[-1]
                        last_child.append_node(lb)
                        if lb_tail is not None:
                            lb_tail_strs = lb_tail.split()
                            lb.tail = lb_tail_strs[0] 

                            parent_copy = append_tail_or_text(' '.join(lb_tail_strs[1:]), parent_copy)

                elif localname in AtomicTokenType.values() + AtomicNonTokenType.values():
                    parent_copy.append_node(e_without_tail)
                    parent_copy = append_tail_or_text(child.tail, parent_copy)                    

                elif localname in SubatomicTagType.values(): # e.g. <expan>, <choice>, <hi>
                    if localname in CompoundTokenType.values(): # this is intended for <hi>, which is also a compound token
                        tokenized = tokenize_subatomic_tags(e_without_tail)
                        if TokenizableElement(parent_copy)._e.child_elements == []:
                            parent_copy.append_node(tokenized._e)

                        elif tokenized._e.last_child is None:
                            parent_copy.append_node(tokenized._e)
                        else:
                            new_e = tokenized._e.last_child.e 
                            first_w = parent_copy.child_elements[0]
                            first_w.append_node(new_e)
                            first_w.child_elements[-1].tail = child.tail        
                    else:
                        new_w = tokenize_subatomic_tags(e_without_tail).e
                        parent_copy.append_node(new_w)
                        parent_copy = append_tail_or_text(child.tail, parent_copy)              
                    
                elif localname in CompoundTokenType.values(): # e.g. <persName>, <orgName>, <roleName>
                    new_w_elem = TokenizableElement.w_factory(parent=e_without_tail)
                    parent_copy.append_node(new_w_elem._e)
                    parent_copy = append_tail_or_text(child.tail, parent_copy)

            return TokenizableElement(parent_copy, final_space=True)
        else:
            if prototoken: 
                new_w = XmlElement.create('w', TEINS)
                new_w.text = prototoken
            else:
                new_w = XmlElement.create('w', TEINS)
 
            for child in subelements:
                new_w.append_node(child)

        return TokenizableElement(new_w, final_space=True)
    
    @property
    def xml_id(self) -> str | None:
        """
        Returns value of the xml:id attribute in the XML file.
        """
        return self.get_attr('id', namespace=XMLNS)

    @xml_id.setter
    def xml_id(self, id_value: str | None) -> None:
        """
        Sets the value of the xml:id attribute in the XML file.
        """
        if id_value is None:
            self._e.remove_attr('id', namespace=XMLNS)
        else:
            self.set_attr('id', id_value, namespace=XMLNS)


