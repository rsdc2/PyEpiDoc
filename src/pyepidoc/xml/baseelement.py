from __future__ import annotations
from typing import (
    List,
    Sequence,
    Callable,
    Optional, 
    Union, 
    Iterable,
    cast,
    overload
)
from copy import deepcopy

from ..shared.classes import Showable, ExtendableSeq, SetRelation
import operator
import re

from lxml import etree 
from lxml.etree import ( 
    _Element,
    _ElementTree, 
    _Comment,
    _ElementUnicodeResult
)

from pyepidoc.shared.classes import Tag
from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.shared import maxone, head
from pyepidoc.xml.utils import localname
from .namespace import Namespace as ns


class BaseElement(Showable):    

    """
    Provides basic XML navigation services, but nothing specific to EpiDoc.
    """
    _e: _Element

    def __eq__(self, other) -> bool:
        if type(other) is not BaseElement \
            and not issubclass(type(other), BaseElement):

            return False
        
        return self.id_internal == other.id_internal

    def __gt__(self, other) -> bool:
        if type(other) is not BaseElement and not issubclass(type(other), BaseElement):
            raise TypeError(f"Other element is of type {type(other)}.")

        if len(self.id_internal) != len(other.id_internal):
            return self._compare_equal_length_ids(
                self.id_internal, 
                other.id_internal, 
                operator.gt
            )

        return self.id_internal[-1] > other.id_internal[-1]

    def __hash__(self) -> int:
        return hash(
            '.'.join(
                [str(id_part) for id_part in self.id_internal]
            )
        )

    @overload
    def __init__(self, e: BaseElement):
        ...

    @overload
    def __init__(self, e: _Element):
        """
        :param e: lxml |_Element|; |_Comment| is subclass of |_Element|
        """
        ...

    def __init__(self, e:Union[_Element, BaseElement]):
        error_msg = (f'Expected type is _Element or BaseElement '
                     f'type or None. Actual type is {type(e)}.')
        
        if not isinstance(e, (_Element, BaseElement)):
            raise TypeError(error_msg)

        if isinstance(e, _Element):
            self._e = e

        elif isinstance(e, BaseElement):
            self._e = e.e

    def __lt__(self, other) -> bool:
        if type(other) is not BaseElement and not issubclass(type(other), BaseElement):
            raise TypeError(f"Previous element is of type {type(other)}.")

        if len(self.id_internal) != len(other.id_internal):
            return self._compare_equal_length_ids(self.id_internal, other.id_internal, operator.lt)

        return self.id_internal[-1] < other.id_internal[-1]

    def __repr__(self) -> str:
        
        return f"BaseElement({self.tag}: '{self.text_desc_compressed_whitespace.strip()}{self.tail.strip() if self.tail is not None else ''}')"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def ancestor_count(self) -> int:

        """
        Return the number of ancestors of the current 
        element, excluding self.
        """

        return len(self.ancestors_excl_self)

    def get_ancestors_incl_self(self) -> ExtendableSeq[BaseElement]:

        """
        Returns an |ExtendableSeq| of parent |BaseElement|
        ordered by closest parent to furthest parent.
        """

        def _climb(acc:ExtendableSeq[BaseElement], element:Optional[BaseElement]) -> ExtendableSeq[BaseElement]:
            if element is None:
                return acc
            elif isinstance(element, BaseElement) or issubclass(type(element), BaseElement):
                acc += [element]
                return _climb(acc, element.parent)
            
            raise TypeError('element is of the wrong type.')

        init_list = cast(ExtendableSeq[BaseElement], []) 
        return _climb(acc=init_list, element=self)

    @property
    def ancestors_excl_self(self) -> ExtendableSeq[BaseElement]:
        ancestors = self.get_ancestors_incl_self()
        if len(ancestors) > 0:
            return cast(ExtendableSeq[BaseElement], ancestors[1:])
        return cast(ExtendableSeq[BaseElement], [])

    @property
    def attrs(self) -> dict[str, str]:
        """
        Return the attributes of the element as a dictionary
        """

        return {k: v for k, v in self.e.attrib}

    def _clean_text(self, text: str):

        """
        Remove newline, space and tab characters 
        """
        return (text.strip()
            .replace('\n', '')
            .replace(' ', '')
            .replace('\t', ''))

    @property 
    def child_comments(self) -> Sequence[BaseElement]:
        return [child for child in self.child_nodes
                if isinstance(child, _Comment)]

    @property
    def child_elements(self) -> Sequence[BaseElement]:
        if self._e is None:
            return []
            
        _children: list[_Element] = self._e.getchildren()
        return [BaseElement(child) for child in _children]

    @property
    def child_node_names(self) -> list[str]:
        children = self.child_nodes
        return list(map(localname, children))

    @property
    def child_nodes(self) -> list[_Element | _ElementUnicodeResult]:
        return self.xpath('child::node()')
    
    @property
    def children(self) -> Sequence[BaseElement]:
        return self.child_elements

    @staticmethod
    def _compile_attribs(attribs: Optional[dict[str, str]]) -> str:
        """
        Represent a dictionary of attributes as an XPath string
        """
        if attribs is None:
            return ''
        return '[' + ''.join([f"@{k}='{attribs[k]}'" 
                              for k in attribs]) + ']'
    
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

    def contains(self, localname: str) -> bool:
        """
        Return True if any descendant node has an element with the tag
        given in `localname`
        """

        return len(self.desc_elems_by_local_name(localname=localname)) > 0
    
    def deepcopy(self) -> BaseElement:

        return BaseElement(deepcopy(self._e))
    
    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self.get_ancestors_incl_self()
            if type(parent.parent) is BaseElement])

    @property
    def desc_comments(self) -> Sequence[_Comment]:
        if self.e is None:
            return []
        
        return [item for item in self.e.iterdescendants(None)
                 if isinstance(item, _Comment)]

    @property
    def desc_elems(self) -> list[BaseElement]:
        """
        :return: a list of all descendant |Element|s.
        Does not return any text or comment nodes.
        """

        if self._e is None:
            return []
        
        return [BaseElement(item) 
                for item in self.e.iterdescendants(tag=None)
                 if isinstance(item, _Element)]

    def desc_elems_by_local_name(self, localname: str) -> list[BaseElement]:
        """
        Return a list of all the descendant elements
        with the localname matching `localname`
        """
        return [elem for elem in self.desc_elems
                if elem.tag.name == localname]

    @property
    def desc_elem_names(self) -> list[str]:
        """
        :return: list of names of all descendant nodes
        """
        return [elem.localname for elem in self.desc_elems]

    @property
    def desc_elem_name_set(self) -> set[str]:
        """
        :return: set of names of all descendant nodes
        """
        return set(self.desc_elem_names)

    @property
    def desc_nodes(self) -> list[_Element | _ElementUnicodeResult | _Comment]:

        """
        Return all descendant nodes of any kind including comments
        """

        return self._e.xpath('.//node()')
    
    @property
    def desc_non_comments(self) -> list[_Element | _ElementUnicodeResult]:

        """
        Return all descendant nodes excluding comments
        """
        return [node for node in self.desc_nodes
                if not isinstance(node, _Comment)]

    @property
    def dict_desc(self) -> dict:
        if self._e is None:
            return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': dict()}

        return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': self._e.attrib}

    @property
    def e(self) -> _Element:
        return self._e

    @property
    def e_type(self) -> type:
        return type(self._e)

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

    @property
    def first_child(self) -> Optional[BaseElement]:
        if self.child_elements == []:
            return None
        
        return self.child_elements[0]

    @staticmethod
    def from_xml_str(xml_str: str) -> BaseElement:
        """
        Return an element from an XML string
        """
        parser = etree.XMLParser(
            load_dtd=False,
            resolve_entities=False,
            remove_blank_text=False,
            
        )
        lxml_elem: _Element = etree.fromstring(
            text=xml_str, 
            parser=parser
        )

        return BaseElement(lxml_elem)

    def has_parent(self, localname: str) -> bool:
        return self.parent is not None and self.parent.localname == localname

    @property
    def last_child(self) -> Optional[BaseElement]:
        if self.child_elements == []:
            return None
        
        return self.child_elements[-1]

    def get_attrib(
        self, 
        attribname:str, 
        namespace:Optional[str]=None
    ) -> Optional[str]:

        """
        Returns the value of the named attribute.
        """
    
        if self._e is None:
            return ''

        return self._e.attrib.get(ns().give_ns(attribname, namespace), None)

    def get_desc(self, 
        elemnames: Union[list[str], str], 
        attribs: Optional[dict[str, str]]=None,
        ns_prefix: str="ns:",
        namespace: str=TEINS
    ) -> list[_Element]:

        """
        Return all descendant elements with the names 
        given in elemnames and attributes given in 
        attribs
        """

        if self.e is None: 
            return []
        if type(elemnames) is str:
            _elemnames = [elemnames]
        elif type(elemnames) is list:
            _elemnames = elemnames
        else:
            raise TypeError("elemnames has incorrect type.")

        xpathstr = ' | '.join([f".//{ns_prefix}{elemname}" + self._compile_attribs(attribs) for elemname in _elemnames])

        xpathRes = (self
            .e
            .xpath(xpathstr, namespaces={'ns': namespace})
        )

        if type(xpathRes) is list:
            return cast(list[_Element], xpathRes)

        raise TypeError('XPath result is of the wrong type.')

    def get_desc_tei_elem(self, 
        elem_name: str, 
        attribs: dict[str, str] | None = None,
        throw_if_more_than_one: bool = False
    ) -> BaseElement | None:
        
        """
        Get first descendant TEI namespace element with the specified
        name and attributes
        """

        return maxone(
            lst=self.get_desc_tei_elems([elem_name], attribs=attribs),
            defaultval=None,
            throw_if_more_than_one=throw_if_more_than_one
        )

    def get_desc_tei_elems(self, 
        elem_names: list[str] | str, 
        attribs: dict[str, str] | None = None
    ) -> list[BaseElement]:
        
        """
        Get all the descendant elements within a particular
        set of names in the TEI namespace.
        """

        return [BaseElement(desc) 
            for desc in self.get_desc(elemnames=elem_names, attribs=attribs)]
    
    def get_div_descendants(
        self, 
        divtype: str, 
        lang: Optional[str]=None
    ) -> list[_Element]:

        if self.e is None: 
            return []

        if not lang:
            return cast(list[_Element], self.e.xpath(f".//ns:div[@type='{divtype}']", namespaces={'ns': TEINS}) )

        elif lang:
            return cast(list[_Element], self.e.xpath(
                f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': TEINS, 'xml': XMLNS}) 
            )
        
        return []

    def get_first_parent_by_name(
            self, 
            parent_tag_names:list[str]) -> Optional[BaseElement]:

        return maxone(
            lst=self.get_ancestors_by_name(parent_tag_names), 
            defaultval=None, 
            throw_if_more_than_one=False
        )
    
    def get_first_desc_elem(self) -> Optional[BaseElement]:
        """
        Return the first descendant element
        """

        descs = cast(list[_Element], self.xpath("descendant::*", dict()))
        if descs == []:
            return None
        
        return BaseElement(descs[0])

    def get_ancestors_by_name(
            self,  
            ancestor_names:list[str]) -> Sequence[BaseElement]:
        
        return [ancestor for ancestor in self.get_ancestors_incl_self()
            if ancestor.tag.name in ancestor_names]

    def has_ancestor_by_name(self, localname: str) -> bool:
        """
        :param localname: the localname of the ancestor element
        that is being sought.
        """
        names = map(lambda elem: elem.localname, self.ancestors_excl_self)
        return localname in names

    def has_ancestors_by_names(
            self, 
            names: list[str], 
            setrelation: Callable[[set[str], set[str]], bool] = SetRelation.intersection
            ) -> bool:
        
        """
        Return true if the set relation function returns true
        for the set of names and the set of ancestors
        """
        
        ancestor_names = map(lambda elem: elem.localname, self.ancestors_excl_self)
        return setrelation(set(names), set(ancestor_names))

    def has_attrib(self, attribname:str) -> bool:
        if self._e is None:
            return False

        return attribname in self._e.attrib.keys()

    @property
    def id_internal(self) -> list[int]:

        """
        Unique computed element id based on hierarchical position in the XML document. 
        """
        
        def _recfunc(acc:list[int], element:Optional[BaseElement]) -> list[int]:
            if element is None:
                return acc 

            if element.e is None:
                return acc
            
            parent = element.e.getparent()
            if parent is None:
                return acc
            
            return _recfunc([parent.index(element.e)] + acc, element.parent)

        return _recfunc([], self)

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
    def has_only_whitespace(self) -> bool:

        """
        Return True if the element contains only comments 
        and whitespace
        """

        non_comment_nodes = self.desc_non_comments
        element_nodes = [node for node in non_comment_nodes
                            if isinstance(node, _Element)]
        text_nodes = [node for node in non_comment_nodes
                            if isinstance(node, _ElementUnicodeResult)]
        
        if len(element_nodes) == 0:
            return ''.join(text_nodes).strip() == ''
        
        return False

    @property
    def localname(self) -> str:
        """
        :return: Name without namespace as |str|
        """
        if self._e is None:
            return ''
        if isinstance(self.e, _Comment):
            return "Comment"
        return ns.remove_ns(self._e.tag)

    @property
    def next_siblings(self) -> list[BaseElement]:

        """
        :return: next sibling |BaseElement|s, excluding text nodes
        """
        next_sibs = self.xpath('following-sibling::*')

        return [BaseElement(sib) for sib in next_sibs
                if type(sib) is _Element]

    @property
    def parent(self) -> Optional[BaseElement]:
        if self._e is None:
            return None

        if type(self._e.getparent()) is _Element:    
            return BaseElement(self._e.getparent())
        elif self._e.getparent() is None:
            return None
        else:
            raise TypeError('Parent is of incorrect type.')


    @property
    def previous_sibling(self) -> Optional[BaseElement]:
        if self._e is None:
            return None

        _prev = self._e.getprevious()
        if isinstance(_prev, _Element):
            return BaseElement(_prev)
        elif _prev is None:
            return None

        raise TypeError(f"Previous element is of type {type(_prev)}.")

    @property 
    def previous_siblings(self) -> List[BaseElement]:
        """
        Returns previous sibling non-text elements
        """

        prev_sibs = self.xpath('preceding-sibling::*')

        return [BaseElement(sib) for sib in prev_sibs 
                if type(sib) is _Element]
    
    def prettify_element_with_pyepidoc(
            element: BaseElement,
            space_unit: str,
            multiplier: int = 4,
            exclude: list[str] | None = None) -> BaseElement:
        """
        Prettify a BaseElement and all descendant elements

        :param exclude: list of element names whose children 
            should not be prettified
        """
        if exclude is None: exclude = []

        
        # Iterate through descendant elements (incl. comments)
        for desc in [element] + list(element.desc_elems): 

            # Don't do anything to descdendant nodes containing @xml:space = "preserve"
            if desc.xmlspace_preserve_in_ancestors:
                continue

            # Do not prettify element if an ancestor element is in the set of element names to exclude
            if set(map(lambda d: d.localname, desc.ancestors_excl_self)).intersection(set(exclude)) != set():
                continue

            # Do not prettify if the next sibling is a comment
            if isinstance(desc.e.getnext(), _Comment):
                continue
            
            # Do not prettify a comment if its siblings are only 
            # comments
            if isinstance(desc.e, _Comment) and \
                desc.parent is not None and \
                len(desc.parent.child_comments) == len(desc.parent.child_nodes):
                continue

            # Only insert a new line and tab as first child if there are 
            # child elements and the first child is not a comment
            if len(desc.child_elements) > 0 and \
                desc.localname not in exclude and \
                type(desc.children[0].e) is not _Comment:
                
                desc.text = '\n' + \
                    (desc.ancestor_count + 1) * multiplier * space_unit + \
                    (desc.text or '').strip()

            # Add new line and tabs after tag
            if desc.parent is not None and \
                desc.parent.last_child is not None and \
                    desc.parent.last_child.id_internal == desc.id_internal:
                
                # If last child, add one fewer tab so that closing tag
                # has correct alignment
                tail_to_append = '\n' + (desc.ancestor_count - 1) * space_unit * multiplier

                if desc.tail is None:
                    desc.tail = tail_to_append
                else:
                    desc.tail = desc.tail.strip() + tail_to_append
            else:
                tail_to_append = '\n' + (desc.ancestor_count) * space_unit * multiplier
                if desc.tail is None:
                    desc.tail = tail_to_append
                else:
                    desc.tail = desc.tail.strip() + tail_to_append

        return element

    def remove_attr(
            self, 
            attr_name: str, 
            namespace: str | None = None,
            throw_if_not_found: bool = False) -> BaseElement:
        """
        Remove an XML attribute with name `attr_name` in
        namespace `namespace`.

        :param throw_if_not_found: Throw an error if the attribute 
        does not exist
        """

        name_with_ns = ns.give_ns(attr_name, namespace)
        if not name_with_ns in self._e.attrib.keys():
            if throw_if_not_found:
                raise AttributeError(f'Attribute {name_with_ns} not found.')
            else:
                return self
        self._e.attrib.pop(name_with_ns)
        return self

    def remove_children(self) -> BaseElement:
        """
        Remove all children, including text, 
        but keep all other properties the same
        """

        for child in self.child_elements:
            self._e.remove(child._e)
        
        self.text = ""

        return self

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
        attribname: str, 
        value: str, 
        namespace: Optional[str] = None
        ) -> None:
        
        if self._e is None:
            return

        self._e.attrib[ns.give_ns(attribname, namespace)] = value

    @property
    def tag(self) -> Tag:

        """
        Return the element tag as a nemedtuple
        (namespace, name).
        """

        if isinstance(self._e, _Comment):
            return Tag("", "Comment")

        if self._e is None: 
            return Tag(None, None)

        etag = self._e.tag
        match = re.search(r'(\{(.+)\})?(.+)', etag)

        if match is None:
            return Tag(None, None)

        if len(match.groups()) != 3:
            raise ValueError('Invalid element name')

        if match.groups()[0] is None:    # i.e. no namespace: check
            return Tag('', etag)
        else:
            return Tag(match.groups()[1], match.groups()[2])

    @property
    def tail(self) -> Optional[str]:
        return self._e.tail if self._e is not None else ''

    @tail.setter
    def tail(self, value: str):
        if self._e is None:
            return

        self._e.tail = value    # type: ignore

    @property
    def text(self) -> str | None:
        if self._e is None:
            return ''

        if self._e.text is None:
            return ''
            
        return self._e.text

    @text.setter
    def text(self, value: str | None):
        if self._e is None:
            return

        self._e.text = value    # type: ignore

    @property
    def text_desc(self) -> str:
        if self._e is None: 
            return ''
        return ''.join(self._e.xpath('.//text()'))

    @property
    def text_desc_compressed_whitespace(self) -> str:
        pattern = r'[\t\s\n]+'
        return re.sub(pattern, ' ', self.text_desc)

    @property
    def xml_byte_str(self) -> bytes:
        """
        Return the element as a byte string
        """
        return etree.tostring(
            self._e, 
            method='xml', # type: ignore
            pretty_print=True # type: ignore
        ) 
    
    @property
    def xmlspace_preserve(self) -> bool:
        """
        Return true if @xml:space = "preserve"
        """

        return self.get_attrib("space", XMLNS) == "preserve"

    @property
    def xmlspace_preserve_in_ancestors(self) -> bool:
        """
        Return true if @xml:space = "preserve" in any ancestors
        excluding self
        """

        for ancestor in self.ancestors_excl_self:
            if ancestor.xmlspace_preserve:
                return True
            
        return False

    @property
    def xml_str(self) -> str:

        """
        Return the element as a unicode string
        """
        return etree.tostring(
            self._e, 
            method='xml', # type: ignore
            encoding='unicode', # type: ignore
            pretty_print=False # type: ignore
        )
    
    def xpath(
            self, 
            xpathstr: str, 
            namespaces: dict[str, str]={'ns': TEINS}
            ) -> list[_Element | _ElementUnicodeResult]:
        """
        Apply XPath expression to the current element, in which 
        the prefix 'ns' corresponds to the namespace
        "http://www.tei-c.org/ns/1.0"
        """

        result = self.e.xpath(xpathstr, namespaces=namespaces)

        # NB the cast won't necessarily be correct for all test cases
        return list[Union[_Element,_ElementUnicodeResult]](result)
    
    def xpath_bool(
            self, 
            xpathstr: str, 
            namespaces: dict[str, str]={'ns': TEINS}) -> bool:
        
        """
        Returns the result of an xpath boolean evaluation.
        Returns False if a boolean is not returned.
        """

        result = self.e.xpath(xpathstr, namespaces=namespaces)

        if type(result) is bool:
            return result
    
        return False
    
    def xpath_float(
            self, 
            xpathstr: str, 
            namespaces: dict[str, str]={'ns': TEINS}) -> Optional[float]:
        
        """
        Returns the result of an xpath boolean evaluation.
        Returns False if a boolean is not returned.
        """

        result = self.e.xpath(xpathstr, namespaces=namespaces)

        if type(result) is float:
            return result
    
        return None
    