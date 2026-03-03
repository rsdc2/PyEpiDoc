from __future__ import annotations

from typing import Sequence, overload, Optional

from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.shared.namespaces import TEINS, XMLNS

from pyepidoc.shared.iterables import maxone


class TeiElement:

    """
    Provides services to all TeiElement objects
    """

    _e: XmlElement

    @overload
    def __init__(self, e: TeiElement):
        ...

    @overload
    def __init__(self, e: XmlElement):
        ...

    def __init__(self, e: XmlElement | TeiElement):
        error_msg = (f'Expected type is XmlElement or TeiElement '
                     f'type or None. Actual type is {type(e)}.')
        
        if not isinstance(e, (XmlElement, TeiElement)):
            raise TypeError(error_msg)
        elif isinstance(e, XmlElement):
            self._e = e
        elif isinstance(e, TeiElement):
            self._e = e._e

    def append(self, tei_element: TeiElement) -> TeiElement:
        element = self._e.append_node(tei_element._e)
        return TeiElement(element)

    @property
    def child_elems(self) -> Sequence[TeiElement]:
        return [TeiElement(child) for child in self._e.child_elements]

    @classmethod
    def create(cls, localname: str, attrs: dict[str, str] = dict()) -> TeiElement:
        """
        Create a new Element in the TEI namespace with local name 
        `localname` and `attrs`
        """

        elem = XmlElement.create(localname, TEINS, attrs)
        return TeiElement(elem)
    
    def find_next_sibling(self) -> TeiElement | None:

        """
        Finds the next non-comment sibling |TeiElement|.
        """
        next_sibling_element = self._e.next_element
        if isinstance(next_sibling_element, XmlElement):
            return TeiElement(next_sibling_element)

        return None

    def get_attr(
            self, 
            attribname: str, 
            namespace: str | None=None
        ) -> str | None:

        return self._e.get_attr(attribname, namespace)
    
    def get_descendant_tei_element(
            self, 
            elem_name: str, 
            attribs: dict[str, str] | None = None,
            throw_if_more_than_one: bool = False
        ) -> TeiElement | None:
        
        """
        Get first descendant TEI namespace element with the specified
        name and attributes
        """

        return maxone(
            lst=self.get_desc([elem_name], attribs=attribs),
            defaultval=None,
            throw_if_more_than_one=throw_if_more_than_one
        )

    def get_desc(
            self, 
            elem_names: list[str] | str, 
            attribs: dict[str, str] | None = None
        ) -> list[TeiElement]:
        
        """
        Get all the descendant elements within a particular
        set of names in the TEI namespace.

        :param elem_names: the local names of the elements wanted
        :param attribs: the attributes of the elements wanted
        """

        return [TeiElement(desc) 
            for desc in self._e.get_desc(elem_names=elem_names, attribs=attribs, namespace=TEINS)]
    
    def get_div_descendants(
            self, 
            divtype: str, 
            level: str = '',
            lang: str | None = None
        ) -> list[XmlElement]:

        if not lang:
            xpath_str = f".//ns:div{level}[@type='{divtype}']"
            descendants = self._e.xpath(xpath_str, namespaces={'ns': TEINS})
        elif lang:
            xml_str = f".//ns:div{level}[@type='{divtype} @xml:lang='{lang}']"
            descendants = self._e.xpath(xml_str, namespaces={'ns': TEINS, 'xml': XMLNS})

        return [desc for desc in descendants 
                if isinstance(desc, XmlElement)]

    def get_div_descendants_by_type(
        self, 
        divtype: str, 
        lang: str | None = None
    ) -> list[XmlElement]:

        """
        :param divtype: the value of the @type attribute of 
        the `<div/>`, e.g. "edition" or "translation"

        :param lang: the value of the @xml:lang attibute
        of the `<div/>` element. If None, treated as not specified.
        
        :return: a list of descendant elements where the
        `@type` attribute matches `divtype`.
        """
        if lang is None:
            descendants = self._e.xpath(f".//ns:div[@type='{divtype}']", 
                    namespaces={'ns': TEINS})

        elif lang is not None:
            descendants = self._e.xpath(
                f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': TEINS, 'xml': XMLNS})
        
        return [node for node in descendants 
            if isinstance(node, XmlElement)]

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

        self._e.text = value

    def set_attr(
        self, 
        attribname: str, 
        value: str | None, 
        namespace: Optional[str]=None) -> None:
        
        self._e.set_attr(attribname, value, namespace)
    
    def __repr__(self) -> str:
        return f"TeiElement({self._e.tag}: '{self._e.text_desc_compressed_whitespace.strip()}{self._e.tail.strip() if self._e.tail is not None else ''}')"

    def __str__(self) -> str:
        return self.__repr__()