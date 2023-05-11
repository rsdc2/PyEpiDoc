from __future__ import annotations
from typing import (
    List,
    Sequence,
    Callable,
    Optional, 
    Union, 
    Iterable,
    cast
)

from .types import Showable, ExtendableSeq
from .baseelement import BaseElement

from copy import deepcopy
from functools import reduce, cached_property
import operator
import re

from lxml import etree # type: ignore
from lxml.etree import ( # type: ignore
    _Element,
    _ElementTree, 
    _Comment as C,
    _Comment,
    _ElementUnicodeResult
)

from .namespace import Namespace as ns

from ..constants import NS, XMLNS, SubsumableRels
from ..base.types import Tag
from ..epidoc.epidoctypes import (
    whitespace, 
    AtomicTokenType, 
    CompoundTokenType, 
    BoundaryType
)
from .root import Root
from ..utils import maxone, maxoneT, head, last


class Element(BaseElement, Showable):    

    _final_space: bool = False

    """
    Provides basic services for all EpiDoc elements.
    """

    def __add__(self, other:Optional[Element]) -> list[Element]:
        """
        Handles appending |Element|s.
        """

        # Handle cases where other is None
        if other is None:
            return [self]

        if type(other) not in [Element]:
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
                return [Element(self_e)]

            if self._subsumable_by(other):
                self_e.tail = other.text
                other_e.text = ''
                other_e.insert(0, self_e)
                
                return [Element(other_e)]
            
            return [self, other]

        # Handle like tags        
        if self.tag == other.tag:
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
                if self._can_subsume(first_child):

                    for child in list(other_e):
                        self_e.append(child)
                    return [Element(self_e)]

            # Look inside self to see if other tag can 
            # subsume it;
            # if so, merge tags
            if (tail is None or tail == '') and last_child is not None:
                if other._can_subsume(last_child):
                    for child in list(other_e):
                        self_e.append(child)
                    return [Element(self_e)]
                    
        return [Element(self_e), Element(other_e)]


    def __init__(
        self, 
        e:Optional[Union[_Element, Element, BaseElement]] = None,
        final_space:bool = False
    ):
        error_msg = f'e should be _Element or Element type or None. Type is {type(e)}.'

        if type(e) not in [_Element, Element, BaseElement] and e is not None and not issubclass(type(e), BaseElement):
            raise TypeError(error_msg)

        if type(e) is _Element:
            self._e = e
        elif type(e) is Element:
            self._e = e.e
        elif type(e) is BaseElement:
            self._e = e.e
        elif e is None:
            self._e = None
        elif issubclass(type(e), BaseElement):
            self._e = e.e

        self._final_space = final_space

    def __repr__(self):
        tail = '' if self.tail is None else self.tail
        content = ''.join([
            # '{', self.tag.ns, '}', 
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
    def abbr_elems(self) -> Sequence[Element]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [Element(abbr) for abbr in self.get_desc_elems_by_name('abbr') 
            if abbr.text is not None]
        
    @property
    def has_abbr(self) -> bool:
        """
        Returns True if the element contains an 
        abbreviation, i.e. <abbr>.
        """
        
        return len(self.abbr_elems) > 0

    @property
    def is_edition(self) -> bool:
        """
        Returns True if the element is an edition <div>.
        """

        return self.name_no_namespace == 'div' \
            and self.get_attrib('type') == 'edition'

    @property
    def am_elems(self) -> Sequence[Element]:
        """
        Returns a |list| of abbreviation marker elements <am>.
        See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html,
        last accessed 2023-04-13.
        """

        return [Element(abbr) for abbr in self.get_desc_elems_by_name('am')]

    def append_space(self) -> Element:
        """Appends a space to the element in place."""

        if self._e is None:
            return self

        if self._e.getnext() is None:
            return self

        if self._e.tail is None:
            self._e.tail = ' '
            return self
        
        self._e.tail = self._e.tail + ' '
        return self

    @property
    def left_bound(self) -> bool:
        """
        Return False if self is <lb break='no'>, otherwise return True.
        First child only counted if the element has no text.
        Used for element addition in __add__ method.
        """

        if self.name_no_namespace == 'lb' and self.get_attrib('break') == 'no':
            return False
        
        first_child = head(self.child_elems)
        if first_child is not None and (self.text == '' or self.text is None):
            if  first_child.name_no_namespace == 'lb' and first_child.get_attrib('break') == 'no':
                return False
            
        return True

    @property
    def right_bound(self) -> bool:
        """
        Return False if self or last child is <lb break='no'>, otherwise return True.
        Last child only counted if the last child has no tail.
        Used for element addition in __add__ method.
        """

        if self.name_no_namespace == 'lb' and self.get_attrib('break') == 'no':
            return False

        last_child = last(self.child_elems)
        if last_child is not None and (last_child.tail == '' or last_child.tail is None):
            if  last_child.name_no_namespace == 'lb' and last_child.get_attrib('break') == 'no':
                return False

        return self._final_space

    @property
    def child_elems(self) -> list[Element]:
        return [Element(child) for child in self.children]
    
    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self.parents 
            if type(parent.parent) is Element])

    @property
    def dict_desc(self) -> dict:
        if self._e is None:
            return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': dict()}

        return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': self._e.attrib}

    @property
    def e(self) -> Optional[_Element]:
        return self._e

    @property
    def ex_elems(self) -> Sequence[Element]:
        """
        Return all abbreviation expansions (minus abbreviation) 
        as a |list| of |Element|.
        """

        return [Element(ex) for ex in self.get_desc_elems_by_name('ex')]

    @property
    def expan_elems(self) -> Sequence[Element]:
        """
        Return all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [Element(expan) for expan in self.get_desc_elems_by_name('expan')]

    @property
    def final_tailtoken_boundary(self) -> bool:
        """
        Returns True if the final element of the tail is a whitespace,
        implying a word break at the end of the element.
        """

        if self.tail is None: 
            return False
        
        if self.name_no_namespace == 'lb' and self.get_attrib('break') == 'no':
            return False
        
        if self.tail == '':
            return False

        return self.tail[-1] in whitespace
    
    @property
    def _first_internal_protoword(self) -> str:
        if self._internal_prototokens == []:
            return ''
        return self._internal_prototokens[0]

    @property
    def first_internal_word_element(self) -> Optional[Element]:
        if self.internal_token_elements == []:
            return None
        
        return self.internal_token_elements[0]

    @property
    def gaps(self) -> list[Element]:
        return [Element(gap) for gap in self.get_desc('gap')]
    
    @property
    def id_internal(self) -> list[int]:

        """
        Unique computed element id based on hierarchical position in the XML document. 
        """
        
        def _recfunc(acc:list[int], element:Optional[Element]) -> list[int]:
            if element is None:
                return acc 

            if element.e is None:
                return acc
            
            if element.e.getparent() is None:
                return acc

            return _recfunc([element.e.getparent().index(element.e)] + acc, element.parent)

        return _recfunc([], self)

    @cached_property
    def id_isic(self) -> str:
        if self._e is None:
            return ""

        xpathres = self._e.xpath(f'preceding::x:idno[@type="filename"]', namespaces={"x": NS}) 
        
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
            if self.tag.name in BoundaryType.values():
                return []
            
            return self._internal_tokens

        if self.tail_completer is not None:
            if self.tag.name in BoundaryType.values():
                return [self.tail_completer]


            return self._internal_tokens[:-1] + [maxoneT(self._internal_tokens[-1:], '') + self.tail_completer]
            
        return []

    @property
    def _internal_tokens(self) -> list[str]:
        if self.text_desc is None:
            return []

        return self.text_desc.split()

    @property
    def internal_token_elements(self) -> list[Element]:

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
                child.tail = re.sub(r'[\n\s\t]+', ' ', tail)
                return child

            def remove_newlines_from_text(child: _Element) -> _Element:
                if child.text is None:
                    return child

                text:str = child.text
                child.text = re.sub(r'[\n\s\t]+', ' ', text)
                return child

            _e = deepcopy(e)
            children:list[_Element] = [deepcopy(child) for child in list(e)]
            
            for child in list(_e):
                _e.remove(child)

            children_with_new_tails = list(map(remove_newlines_from_tail, children))     
            children_with_new_text = list(map(remove_newlines_from_text, children_with_new_tails))

            for child in children_with_new_text:
                _e.append(child)

            return _e      
            
        def make_internal_token(e: _Element) -> list[Element]:

            """TODO merge with w_factory"""

            _e = deepcopy(e)
            _e.tail = self.tail_completer
            _element = Element(_e)

            if _element.tag.name in BoundaryType.values():
                internalprotowords = _element._internal_prototokens
                if internalprotowords == []:
                    return [Element(_e, final_space=True)]

                if len(internalprotowords) == 1:
                    _e.tail = ''
                    elems = Element(_e) + Element.w_factory(internalprotowords[0])

                    # Make sure there is a bound to the right if there are multiple tokens in the tail
                    if len(self.tail_token_elements) > 0:
                        elems[-1]._final_space = True
                    return elems
                
                raise ValueError("More than 1 protoword.")

            elif _element.tag.name in AtomicTokenType.values():            
                return [_element]

            elif _element.tag.name in CompoundTokenType.values():
                
                w = Element.w_factory(parent=_element._e)
                return [w]
            
            w = Element.w_factory(subelements=[_e])

            if e.tail is not None and e.tail[-1] in ' ':
                w._final_space = True
            
            return [w]

        e = remove_internal_extraneous_whitespace(self._e)
        return make_internal_token(e)

    @property
    def _join_to_next(self) -> bool:
        return len(self.next_no_spaces) > 1

    @property
    def _join_to_prev(self) -> bool:
        prev_sibling = self.previous_sibling
        
        if prev_sibling is None:
            return False
        
        return Element(prev_sibling)._join_to_next

    @property
    def lb_in_preceding_or_ancestor(self) -> Optional[_Element]:

        """
        Returns any preceding or |_Element| containing an
        <lb> element.
        cf. https://www.w3.org/TR/1999/REC-xpath-19991116/#axes
        last accessed 2023-04-20.
        """

        def get_preceding_lb(elem:Element) -> list[_Element]:
            
            result = elem.xpath('preceding::*[descendant-or-self::ns:lb]')
            if result == []:
                if elem.parent is None:
                    return []

                return get_preceding_lb(elem.parent)

            return result

        if self._e is None:
            return []

        preceding_lb = last(get_preceding_lb(self))

        if preceding_lb is None:
            return None

        return Element(preceding_lb)

    @property
    def next_no_spaces(self) -> list[Element]:

        """Returns a list of the next |Element| not 
        separated by whitespace."""

        def lb_no_break_next(element:Element) -> bool:
            """Keep going if element is a linebreak with no word break"""
            next_elem = element.next_sibling

            if isinstance(next_elem, Element):
                if next_elem.e is None:
                    return False
                if next_elem.e.tag == ns.give_ns('lb', NS):
                    if next_elem.e.attrib.get('break') == 'no':
                        return True

            return False
                
        def next_no_spaces(acc:list[Element], element:Optional[Element]):
            if not isinstance(element, Element): 
                return acc

            if lb_no_break_next(element):
                return next_no_spaces(acc + [element], element.next_sibling)

            if element.final_tailtoken_boundary:
                return acc + [element]

            return next_no_spaces(acc + [element], element.next_sibling)

        return next_no_spaces([], self)

    @property
    def next_sibling(self) -> Optional[Element]:

        """
        Finds the next non-comment sibling |Element|.
        """

        # TODO: put into base element layer; 
        # previously tried to do this but caused recursion error

        def _get_next(e:Optional[_Element]) -> Optional[_Element]:
            if e is None:
                return None

            _next_sib = e.getnext()

            if type(_next_sib) is C:
                return _get_next(_next_sib)
            if type(_next_sib) is _Element:
                return _next_sib

            return None

        if self._e is None:
            return None

        _next = _get_next(self._e)
        
        if type(_next) is _Element:
            return Element(_next)
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
    def nonword_element(self) -> Optional[Element]:
        if self._e is None:
            return None

        if self.tag.name in BoundaryType.values():
            _e = deepcopy(self._e)
            _e.tail = None
            return Element(_e)
        
        return None

    @property
    def nonword_elements(self) -> list[Element]:
        if self.nonword_element is None:
            return []
        elif type(self.nonword_element) is Element:
            return [self.nonword_element]

        return []

    @property
    def parent(self) -> Optional[Element]:
        if self._e is None:
            return None

        if type(self._e.getparent()) is _Element:    
            return Element(self._e.getparent())
        elif self._e.getparent() is None:
            return None
        else:
            raise TypeError('Parent is of incorrect type.')

    @property
    def preceding_or_ancestor_in_edition(self) -> list[_Element]:

        """
        Returns any preceding or ancestor |_Element| whose
        ancestor is an edition.
        """

        if self._e is None:
            return []

        return self._e.xpath('preceding::*[ancestor::x:div[@type="edition"]]', namespaces={"x": NS}) \
            + self._e.xpath('ancestor::*[ancestor::x:div[@type="edition"]]', namespaces={"x": NS}) 

    @property
    def _prototokens(self) -> list[str]:
        return self._internal_prototokens + self._tail_prototokens

    @property
    def root(self) -> BaseElement:
        return self.parents[-1]

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

    def set_id(self) -> None:
        self.id_xml = self.id_isic + "-" + str(len(self.preceding_or_ancestor_in_edition)) + "0"

    def _can_subsume(self, other:Element) -> bool:
        if type(other) is not Element: 
            return False

        matches = list(filter(
            self._subsume_filterfunc(head=self, dep=other),
            SubsumableRels)
        )
            
        return len(matches) > 0


    def _subsumable_by(self, other:Element) -> bool:
        if type(other) is not Element: 
            return False

        matches = list(filter(self._subsume_filterfunc(head=other, dep=self), SubsumableRels))

        return len(matches) > 0

    @staticmethod
    def _subsume_filterfunc(head:Element, dep:Element):

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
    def tag(self) -> Tag:

        if self._e is None: 
            return Tag(None, None)

        etag = self._e.tag
        match = re.search(r'\{(.+)\}(.+)', etag)

        if match is None:
            return Tag(None, None)

        if len(match.groups()) == 0:
            return etag
        elif len(match.groups()) > 2:
            raise ValueError('Too many namespaces.')

        return Tag(match.groups()[0], match.groups()[1])

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

    @property
    def supplied(self):
        return [Element(supplied) for supplied in self.get_desc('supplied')]

    @property
    def hassupplied(self) -> bool:
        """
        Returns True if token contains a 
        <supplied> tag.
        """

        return len(self.supplied) > 0

    @property
    def _tail_prototokens(self) -> list[str]:

        """Returns separate tokens in the element's tail text, 
        but any elements attached without a space to the element is left
        to be picked up under _internal_prototokens."""

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
    
    @property
    def tail_token_elements(self) -> list[Element]:

        def _make_words(protoword:Optional[str]) -> Element:
            w = Element.w_factory(protoword)
            
            if protoword is not None and protoword[-1] in whitespace:
                w._final_space = True
            return w

        return list(map(_make_words, self._tail_prototokens))
            
    @property
    def text(self) -> str:
        if self._e is None:
            return ''

        if self._e.text is None:
            return ''
            
        return self._e.text

    @text.setter
    def text(self, value:str):
        if self._e is None:
            return

        self._e.text = value

    @property
    def text_desc(self) -> str:
        if self._e is None: 
            return ''
        return ''.join(self._e.xpath('.//text()'))

    @property
    def text_desc_compressed_whitespace(self) -> str:
        pattern = r'[\t\s\n]+'
        return re.sub(pattern, ' ', self.text_desc)

    @staticmethod
    def w_factory(
        prototoken:Optional[str]=None, 
        subelements:list[_Element]=[],
        parent:Optional[_Element]=None,
        final_space:bool=False
    ) -> Element:

        """TODO merge w_factory and make_word functions."""

        def append_tail_or_text(_tail: Optional[str], _parent:_Element) -> _Element:
            if _tail is not None:
                tailword_strs = _tail.split()
                tailtokens = [Element.w_factory(prototoken=tailtoken_str) 
                    for tailtoken_str in tailword_strs]
                [_parent.append(tailtoken.e) for tailtoken in tailtokens] 

            return _parent           

        new_w:_Element
        new_g:_Element

        # Handle interpuncts
        if prototoken is not None and prototoken.strip() in ['·', '·', '❦']:
            namespace = ns.give_ns('g', ns=NS)
            new_g = etree.Element(namespace)

            if prototoken: 
                new_g.text = prototoken
                new_g.set('ref', '#interpunct')

            for e in subelements:
                new_g.append(e)

            g_elem = Element(new_g, final_space=True)
            return g_elem

        elif prototoken is None and parent is not None:
            children:list[_Element] = [deepcopy(e) for e in list(parent)] 
            new_parent:_Element = deepcopy(parent)
            
            # Remove text and children from new_parent
            for child in list(new_parent):
                new_parent.remove(child)
            new_parent.text = None
        
            # Handle the text content of new_parent
            new_parent = append_tail_or_text(parent.text, new_parent)

            # Handle children of new_parent
            for e in children:
                new_e = deepcopy(e)
                new_e.tail = None

                if ns.remove_ns(e.tag) in AtomicTokenType.values() + BoundaryType.values():
                    new_parent.append(new_e)
                    new_parent = append_tail_or_text(e.tail, new_parent)

                elif ns.remove_ns(e.tag) in CompoundTokenType.values(): # e.g. <persName>, <orgName>
                    new_parent.append(Element.w_factory(parent=new_e).e)
                    new_parent = append_tail_or_text(e.tail, new_parent)

                else: # e.g. <expan>
                    namespace = ns.give_ns('w', ns=NS)
                    new_w = etree.Element(namespace)
                    new_w.append(new_e)
                    new_parent.append(new_w)
                    new_parent = append_tail_or_text(e.tail, new_parent)
                    
            return Element(new_parent, final_space=True)
        else:
            if prototoken: 
                namespace = ns.give_ns('w', ns=NS)
                new_w = etree.Element(namespace)
                new_w.text = prototoken
            else:
                new_w = etree.Element(ns.give_ns('w', ns=NS))
 
            for child in subelements:
                new_w.append(child)

        return Element(new_w, final_space=True)

    @property
    def token_elements(self) -> list[Element]:
        return self.internal_token_elements + self.tail_token_elements

    @property
    def xml(self) -> _Element:
        return etree.tostring(self._e)