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

from ..shared_types import Showable, ExtendableSeq
import operator
import re

from lxml import etree 
from lxml.etree import ( 
    _Element,
    _ElementTree, 
    _Comment as C,
    _Comment,
    _ElementUnicodeResult
)

from ..shared_types import Tag

from .namespace import Namespace as ns

from ..constants import NS, XMLNS, SubsumableRels
from ..utils import maxone, maxoneT, head, last


class BaseElement(Showable):    

    """
    Provides basic XML navigation services, but nothing specific to EpiDoc.
    """
    _e: _Element | None

    def __eq__(self, other) -> bool:
        if type(other) is not BaseElement and not issubclass(type(other), BaseElement):
            return False
        
        return self.id_internal == other.id_internal

    def __gt__(self, other) -> bool:
        if type(other) is not BaseElement and not issubclass(type(other), BaseElement):
            raise TypeError(f"Other element is of type {type(other)}.")

        if len(self.id_internal) != len(other.id_internal):
            return self._compare_equal_length_ids(self.id_internal, other.id_internal, operator.gt)

        return self.id_internal[-1] > other.id_internal[-1]

    def __hash__(self) -> int:
        return hash(
            '.'.join(
                [str(id_part) for id_part in self.id_internal]
            )
        )

    @overload
    def __init__(self, e: _Element):
        ...

    @overload
    def __init__(self, e: BaseElement):
        ...

    @overload
    def __init__(self, e: None):
        ...

    def __init__(self, e:Optional[Union[_Element, BaseElement]]=None):
        error_msg = f'Expected type is _Element or BaseElement type or None. Actual type is {type(e)}.'
        
        if not isinstance(e, (_Element, BaseElement)) and e is not None:
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

    def __str__(self):
        return self.text_desc_compressed_whitespace

    @property
    def children(self) -> Sequence[BaseElement]:
        if self._e is None:
            return []
            
        _children: list[_Element] = list(self._e)
        return [BaseElement(child) for child in _children
                    if type(child) is not _Comment]

    @property
    def depth(self) -> int:
        """Returns the number of parents to the root node, where root is 0."""

        return len([parent for parent in self.parents 
            if type(parent.parent) is BaseElement])

    @property
    def desc_comments(self) -> Sequence[_Comment]:
        if self.e is None:
            return []
        
        return [item for item in self.e.iterdescendants()
                 if isinstance(item, _Comment)]

    @property
    def desc_elems(self) -> list[BaseElement]:
        """
        :return: a list of all descendant |Element|s.
        Does not return any text or comment nodes.
        """

        if self._e is None:
            return []

        _descs = self._e.xpath('.//*')
        descs = _descs if type(_descs) is list else []

        return [BaseElement(desc) for desc in descs 
            if isinstance(desc, (_Element))]
    
    @property
    def desc_elem_names(self) -> list[str]:
        """
        :return: list of names of all descendant nodes
        """
        return [elem.local_name for elem in self.desc_elems]

    @property
    def desc_elem_name_set(self) -> set[str]:
        """
        :return: set of names of all descendant nodes
        """
        return set(self.desc_elem_names)

    @property
    def dict_desc(self) -> dict:
        if self._e is None:
            return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': dict()}

        return {'name': self.tag.name, 'ns': self.tag.ns, 'attrs': self._e.attrib}

    @property
    def e(self) -> Optional[_Element]:
        return self._e


    @property
    def first_child(self) -> Optional[BaseElement]:
        if self.children == []:
            return None
        
        return self.children[0]

    @property
    def last_child(self) -> Optional[BaseElement]:
        if self.children == []:
            return None
        
        return self.children[-1]

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

    def get_desc_elems_by_name(self, 
        elem_names:Union[list[str], str], 
        attribs:Optional[dict[str, str]]=None
    ) -> list[BaseElement]:

        return [BaseElement(desc) 
            for desc in self.get_desc(elemnames=elem_names, attribs=attribs)]

    def get_first_parent_by_name(self, parent_tag_names:list[str]) -> Optional[BaseElement]:
        return maxone(
            lst=self.get_parents_by_name(parent_tag_names), 
            defaultval=None, 
            throw_if_more_than_one=False
        )

    def get_parents_by_name(self,  parenttagnames:list[str]) -> Sequence[BaseElement]:
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
    def local_name(self) -> str:
        """
        :return: Name without namespace as |str|
        """
        if self._e is None:
            return ''
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
    def parents(self) -> ExtendableSeq[BaseElement]:

        """
        Returns an |ExtendableSeq| of parent |Element|
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
    def previous_sibling(self) -> Optional[BaseElement]:
        if self._e is None:
            return None

        _prev = self._e.getprevious()
        if type(_prev) is _Element:
            return BaseElement(_prev)
        elif _prev is None:
            return None
        elif type(_prev) is _Comment:
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

    @property
    def tag(self) -> Tag:

        if self._e is None: 
            return Tag(None, None)

        etag = self._e.tag
        match = re.search(r'\{(.+)\}(.+)', etag)

        if match is None:
            return Tag(None, None)

        if len(match.groups()) == 0:    # i.e. no namespace: check
            return Tag('', etag)
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
        if self.e is None: 
            return ''
        
        xpath_res = cast(list[str], self.e.xpath('.//text()'))

        return ''.join(xpath_res)

    @staticmethod
    def _clean_text(text:str):
        return text.strip()\
            .replace('\n', '')\
            .replace(' ', '')\
            .replace('\t', '')

    @staticmethod
    def _compile_attribs(attribs:Optional[dict[str, str]]) -> str:
        if attribs is None:
            return ''
        return '[' + ''.join([f"@{k}='{attribs[k]}'" for k in attribs]) + ']'

    @property
    def xml_byte_str(self) -> bytes:
        if self._e is None:
            raise TypeError("Underlying element is None")
        return etree.tostring(self._e)
    
    def get_desc(self, 
        elemnames:Union[list[str], str], 
        attribs:Optional[dict[str, str]]=None
    ) -> list[_Element]:

        if self.e is None: 
            return []
        if type(elemnames) is str:
            _elemnames = [elemnames]
        elif type(elemnames) is list:
            _elemnames = elemnames
        else:
            raise TypeError("elemnames has incorrect type.")

        xpathstr = ' | '.join([f".//ns:{elemname}" + self._compile_attribs(attribs) for elemname in _elemnames])

        xpathRes = (self
            .e
            .xpath(xpathstr, namespaces={'ns': NS})
        )

        if type(xpathRes) is list:
            return cast(list[_Element], xpathRes)

        raise TypeError('XPath result is of the wrong type.')

    def get_div_descendants(
        self, 
        divtype:str, 
        lang:Optional[str]=None
    ) -> list[_Element]:

        if self.e is None: 
            return []

        if not lang:
            return cast(list[_Element], self.e.xpath(f".//ns:div[@type='{divtype}']", namespaces={'ns': NS}) )

        elif lang:
            return cast(list[_Element], self.e.xpath(
                f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': NS, 'xml': XMLNS}) 
            )
        
        return []

    def xpath(self, xpathstr:str) -> list[_Element | _ElementUnicodeResult]:
        if self.e is None: 
            return []

        # NB the cast won't necessarily be correct for all test cases
        return cast(list[Union[_Element,_ElementUnicodeResult]], self.e.xpath(xpathstr, namespaces={'ns': NS}))