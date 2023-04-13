from __future__ import annotations
from typing import (
    Callable,
    Optional, 
    Union, 
    cast
)

from copy import deepcopy
from functools import reduce, cached_property
import operator
import re
import uuid

from lxml import etree # type: ignore
from lxml.etree import ( # type: ignore
    _Element as _Element, 
    _Comment as C,
    _Comment
)

from .namespace import Namespace as ns

from ..constants import NS, XMLNS, SubsumableRels
from ..epidoc.epidoctypes import (
    Tag, 
    whitespace, 
    AtomicTokenType, 
    CompoundTokenType, 
    BoundaryType
)
from .root import Root
from ..epidoc.empty import EmptyElement
from ..utils import maxone, maxoneT


class Element(Root):    

    def __init__(self, e:Optional[_Element]=None):
        error_msg = f'e should be _Element type or None. Type is {type(e)}.'

        if type(e) is not _Element and e is not None:
            raise TypeError(error_msg)

        self._e = e


    def __gt__(self, other) -> bool:
        if type(other) is not Element:
            raise TypeError(f"Other element is of type {type(other)}.")

        if len(self.id_internal) != len(other.id_internal):
            return self._compare_equal_length_ids(self.id_internal, other.id_internal, operator.gt)

        return self.id_internal[-1] > other.id_internal[-1]

    def __lt__(self, other) -> bool:
        if type(other) is not Element:
            raise TypeError(f"Previous element is of type {type(other)}.")

        if len(self.id_internal) != len(other.id_internal):
            return self._compare_equal_length_ids(self.id_internal, other.id_internal, operator.lt)

        return self.id_internal[-1] < other.id_internal[-1]

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
    def abbr_elems(self) -> list[Element]:
        """
        Return all abbreviation elements as a |list| of |Element|.
        """

        return [abbr for abbr in self.get_desc_elems_by_name('abbr') 
            if abbr.text is not None]
        
    @property
    def has_abbr(self) -> bool:
        """
        Returns True if the token contains an 
        abbreviation, i.e. <abbr>.
        """
        
        return len(self.abbr_elems) > 0

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

    def _can_subsume(self, other:Element) -> bool:
        if type(other) is not Element: 
            return False

        matches = list(filter(self._subsume_filterfunc(head=self, dep=other), SubsumableRels))
            
        return len(matches) > 0

    @property
    def children(self) -> list[Element]:
        if self._e is None:
            return []
            
        _children: list[_Element] = list(self._e)
        return [Element(child) for child in _children
                    if type(child) is not _Comment]

    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self.parents 
            if type(parent.parent) is Element])

    @property
    def desc_elems(self) -> list[Element]:
        """
        Returns a list of all descendant |Element|s.
        Does not return any text nodes.
        """

        if self._e is None:
            return []

        _descs = self._e.xpath('.//*')
        descs = _descs if type(_descs) is list else []

        return [Element(desc) for desc in descs 
            if type(desc) is _Element]

    @property
    def dict_desc(self) -> dict:
        if self._e is None:
            return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': dict()}

        return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': self._e.attrib}

    @property
    def e(self) -> Optional[_Element]:
        return self._e

    @property
    def ex_elems(self) -> list[Element]:
        """
        Return all abbreviation expansions (minus abbreviation) 
        as a |list| of |Element|.
        """

        return [ex for ex in self.get_desc_elems_by_name('ex')]


    @property
    def expan_elems(self) -> list[Element]:
        """
        Return all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [expan for expan in self.get_desc_elems_by_name('expan')]

    @property
    def final_tailtoken_boundary(self) -> bool:
        """
        Returns True if the final element of the tail is a whitespace,
        implying a word break at the end of the element.
        """

        if self.tail is None: 
            return False
        return self.tail[-1] in whitespace

    @property
    def first_child(self) -> Optional[Element]:
        if self.children == []:
            return None
        
        return self.children[0]

    @property
    def last_child(self) -> Optional[Element]:
        if self.children == []:
            return None
        
        return self.children[-1]

    @property
    def _first_internal_protoword(self) -> str:
        if self._internal_prototokens == []:
            return ''
        return self._internal_prototokens[0]

    @property
    def first_internal_word_element(self) -> Union[EmptyElement, Element]:
        if self.internal_token_elements == []:
            return EmptyElement()
        
        return self.internal_token_elements[0]

    @property
    def gaps(self) -> list[Element]:
        return [Element(gap) for gap in self.get_desc('gap')]

    def get_attrib(
        self, 
        attribname:str, 
        namespace:Optional[str]=None
    ) -> Optional[str]:
    
        if self._e is None:
            return ''

        return self._e.attrib.get(ns().give_ns(attribname, namespace), None)

    def get_desc_elems_by_name(self, 
        elem_names:Union[list[str], str], 
        attribs:Optional[dict[str, str]]=None
    ) -> list[Element]:

        return [Element(desc) 
            for desc in self.get_desc(elemnames=elem_names, attribs=attribs)]

    def get_first_parent_by_name(self, parent_tag_names:list[str]) -> Optional[Element]:
        return maxone(
            lst=self.get_parents_by_name(parent_tag_names), 
            defaultval=None, 
            throw_if_more_than_one=False
        )

    def get_parents_by_name(self,  parenttagnames:list[str]) -> list[Element]:
        return [parent for parent in self.parents 
            if parent.tag.name in parenttagnames]

    def has_attrib(self, attribname:str) -> bool:
        if self._e is None:
            return False

        return attribname in self._e.attrib.keys()

    @property
    def id_internal(self) -> list[int]:

        """
        Unique computed element id based on hierarchical position in the XML document. 
        """
        
        def _recfunc(acc:list[int], element:Union[Element, EmptyElement]) -> list[int]:
            if type(element) is EmptyElement:
                return acc 

            if element._e is None:
                return acc
            
            if element._e.getparent() is None:
                return acc

            return _recfunc([element._e.getparent().index(element._e)] + acc, element.parent)

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

        def _remove_internal_extraneous_whitespace(e: _Element):
            """
            Removes extra whitespace from the tails of the elements children:
            means that correct formatting is applied when reformatted. 

            TODO: apply to all descendants
            """

            def _remove_newlines_from_tail(child: _Element):
                if child.tail is None:
                    return child

                # [_remove_newlines_from_tail(child) for child in list(child)]

                tail:str = child.tail
                child.tail = re.sub(r'[\n\s\t]+', ' ', tail)
                return child

            def _remove_newlines_from_text(child: _Element):
                if child.text is None:
                    return child

                text:str = child.text
                child.text = re.sub(r'[\n\s\t]+', ' ', text)
                return child

            _e = deepcopy(e)
            children:list[_Element] = [deepcopy(child) for child in list(e)]
            
            for child in list(_e):
                _e.remove(child)

            children_with_new_tails = list(map(_remove_newlines_from_tail, children))     
            children_with_new_text = list(map(_remove_newlines_from_text, children_with_new_tails))

            for child in children_with_new_text:
                _e.append(child)

            return _e      
            
        def _make_word(e: _Element) -> list[_Element]:

            """TODO merge with w_factory"""

            _e = deepcopy(e)
            _e.tail = self.tail_completer
            _element = Element(_e)

            if _element.tag.name in BoundaryType.values():
                internalprotowords = _element._internal_prototokens
                if internalprotowords == []:
                    return [Element(_e)]

                if len(internalprotowords) == 1:
                    _e.tail = ''
                    return Element(_e) + Element(Element.w_factory(internalprotowords[0]))
                
                raise ValueError("More than 1 protoword.")

            elif _element.tag.name in AtomicTokenType.values():            
                return [_element]

            elif _element.tag.name in CompoundTokenType.values():
                
                w = Element.w_factory(parent=_element._e)
                return [Element(w)]
            
            w = Element.w_factory(subelements=[_e])
            return [Element(w)]

        e = _remove_internal_extraneous_whitespace(self._e)
        return _make_word(e)

    @property
    def _join_to_next(self) -> bool:
        return len(self.next_no_spaces) > 1

    @property
    def name_no_namespace(self) -> str:
        if self._e is None:
            return ''
        return ns.remove_ns(self._e.tag)

    @property
    def next(self) -> Union[Element, EmptyElement]:

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
            return EmptyElement()

        _next = _get_next(self._e)
        
        if type(_next) is _Element:
            return Element(_next)
        elif _next is None:
            return EmptyElement()

        return EmptyElement()

    @property
    def next_no_spaces(self) -> list[Element]:

        """Returns a list of the next |Element| not 
        separated by whitespace."""

        def _lb_no_break_next(element:Element) -> bool:
            """Keep going if element is a linebreak with no word break"""
            next_elem = element.next

            if isinstance(next_elem, Element):
                if next_elem.e is None:
                    return False
                if next_elem.e.tag == ns.give_ns('lb', NS):
                    if next_elem.e.attrib.get('break') == 'no':
                        return True

            return False
                
        def _next_no_spaces(acc:list[Element], element:Element | EmptyElement):
            if not isinstance(element, Element): 
                return acc

            if _lb_no_break_next(element):
                return _next_no_spaces(acc + [element], element.next)

            if element.final_tailtoken_boundary:
                return acc + [element]

            return _next_no_spaces(acc + [element], element.next)

        return _next_no_spaces([], self)

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
    def nonword_element(self) -> Union[Element, EmptyElement]:
        if self._e is None:
            return EmptyElement()

        if self.tag.name in BoundaryType.values():
            _e = deepcopy(self._e)
            _e.tail = None
            return Element(_e)
        
        return EmptyElement()

    @property
    def nonword_elements(self) -> list[Element]:
        if type(self.nonword_element) is EmptyElement:
            return []
        elif type(self.nonword_element) is Element:
            return [self.nonword_element]

        return []

    @property
    def parent(self) -> Union[Element, EmptyElement]:
        if self._e is None:
            return EmptyElement()

        if type(self._e.getparent()) is _Element:    
            return Element(self._e.getparent())
        elif self._e.getparent() is None:
            return EmptyElement()
        else:
            raise TypeError('Parent is of incorrect type.')

    @property
    def parents(self) -> list[Element]:

        def _climb(acc:list[Element], element:Union[Element, EmptyElement]) -> list[Element]:
            if type(element) is EmptyElement:
                return acc
            elif type(element) is Element:
                acc += [element]
                return _climb(acc, element.parent)
            
            raise TypeError('element is of the wrong type.')

        return _climb(acc=[], element=self)

    @property
    def preceding_or_ancestor(self) -> list[_Element]:
        if self._e is None:
            return []

        return self._e.xpath('preceding::*[ancestor::x:div[@type="edition"]]', namespaces={"x": NS}) \
            + self._e.xpath('ancestor::*[ancestor::x:div[@type="edition"]]', namespaces={"x": NS}) 

    @property
    def previous(self) -> Union[Element, EmptyElement]:
        if self._e is None:
            return EmptyElement()

        _prev = self._e.getprevious()
        if type(_prev) is _Element:
            return Element(_prev)
        elif _prev is None:
            return EmptyElement()
        elif type(_prev) is _Comment:
            return EmptyElement()

        raise TypeError(f"Previous element is of type {type(_prev)}.")

    @property
    def _prototokens(self) -> list[str]:
        return self._internal_prototokens + self._tail_prototokens
    
    @property
    def root(self) -> Root:
        return self.parents[-1]

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
        self.id_xml = self.id_isic + "-" + str(len(self.preceding_or_ancestor)) + "0"

    def set_uuid(self) -> None:
        self.id_xml = str(uuid.uuid4())

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
    def tail(self) -> Optional[str]:
        return self._e.tail if self._e is not None else ''

    @tail.setter
    def tail(self, value:str):
        if self._e is None:
            return

        self._e.tail = value

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

    def _subsumable_by(self, other:Element) -> bool:
        if type(other) is not Element: 
            return False

        matches = list(filter(self._subsume_filterfunc(head=other, dep=self), SubsumableRels))

        return len(matches) > 0

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
    def tail_token_elems(self) -> list[Element]:

        def _make_words(protoword:Optional[str]) -> Element:
            w = Element.w_factory(protoword)
            return Element(w)

        return list(map(_make_words, self._tail_prototokens))
            
    @property
    def text(self) -> str:
        if self._e is None:
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
        parent:Optional[_Element]=None
    ) -> _Element:

        """TODO merge w_factory and make_word functions."""

        def append_tail(_tail: Optional[str], _parent:_Element) -> _Element:
            if _tail is not None:
                tailword_strs = _tail.split()
                tailtokens = [Element.w_factory(prototoken=tailtoken_str) 
                    for tailtoken_str in tailword_strs]
                [_parent.append(tailtoken) for tailtoken in tailtokens] 

            return _parent           

        new_w:_Element
        new_g:_Element

        if prototoken == '·':
            namespace = ns.give_ns('g', ns=NS)
            new_g = etree.Element(namespace)

            if prototoken: 
                new_g.text = prototoken

            for e in subelements:
                new_g.append(e)

            return new_g

        elif prototoken is None and parent is not None:
            children:list[_Element] = [deepcopy(e) for e in list(parent)] 
            new_parent:_Element = deepcopy(parent)

            for child in list(new_parent):
                new_parent.remove(child)
            
            for e in children:
                if ns.remove_ns(e.tag) in \
                    AtomicTokenType.values() + BoundaryType.values():
                    new_e = deepcopy(e)
                    new_e.tail = None
                    new_parent.append(new_e)
                    new_parent = append_tail(e.tail, new_parent)
                elif ns.remove_ns(e.tag) in CompoundTokenType.values():
                    new_e = deepcopy(e)
                    new_e.tail = None
                    new_parent.append(Element.w_factory(parent=new_e))
                    new_parent = append_tail(e.tail, new_parent)
                else:
                    namespace = ns.give_ns('w', ns=NS)
                    new_w = etree.Element(namespace)
                    new_w.append(e)
                    new_parent.append(new_w)

            return new_parent
        else:
            if prototoken: 
                namespace = ns.give_ns('w', ns=NS)
                new_w = etree.Element(namespace)
                new_w.text = prototoken
            else:
                new_w = etree.Element(ns.give_ns('w', ns=NS))
 
            for child in subelements:
                new_w.append(child)

        return new_w

    @property
    def token_elements(self) -> list[Element]:
        return self.internal_token_elements + self.tail_token_elems

    @property
    def xml(self) -> _Element:
        return etree.tostring(self._e)

    def __add__(self, other) -> list[Element]:
        if type(other) is EmptyElement:
            return [self]

        if type(other) is not Element:
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
            
        if other.tag != self.tag:
            if self._can_subsume(other):
                self_e.append(other_e)
                return [Element(self_e)]

            if self._subsumable_by(other):
                self_e.tail = other.text
                other_e.text = ''
                other_e.insert(0, self_e)
                
                return [Element(other_e)]
            
            return [self, other]

        new_other_children = list(other_e)

        for child in new_other_children:
            self_e.append(child)

        return [Element(self_e)]

    def __hash__(self) -> int:
        return hash(
            '.'.join(
                [str(id_part) for id_part in self.id_internal]
            )
        )

    def __eq__(self, other) -> bool:
        if type(other) is not Element:
            return False
        
        return self.id_internal == other.id_internal

    def _equalize_id_length(
        self, 
        id1:list[int], 
        id2:list[int]
    ) -> tuple[list[int], list[int]]:
        
        if len(id1) == len(id2):
            return (id1, id2)

        if len(id1) > len(id2):
            newid1 = id1[:len(id2)-1]
            return (newid1, id2)

        if len(id2) > len(id1):
            newid2 = id2[:len(id1)-1]
            return (id1, newid2)

        raise ValueError()

    def _compare_equal_length_ids(
        self, 
        id1:list[int], 
        id2:list[int], 
        op:Callable[[int, int], bool]
    ) -> bool:

        equal_id1, equal_id2 = self._equalize_id_length(id1, id2)

        if equal_id1 == equal_id2:
            return op(len(id1), len(id2))

        return op(equal_id1[-1], equal_id2[-1])
