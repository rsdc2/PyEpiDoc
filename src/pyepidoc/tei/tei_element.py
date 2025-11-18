from __future__ import annotations

from typing import Sequence, cast, overload

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult

from pyepidoc.xml import XmlElement
from pyepidoc.xml.namespace import Namespace as ns
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

    @overload
    def __init__(self, e: _Element):
        """
        :param e: lxml |_Element|; |_Comment| is subclass of |_Element|
        """
        ...

    def __init__(self, e: _Element | XmlElement):
        error_msg = (f'Expected type is _Element or BaseElement '
                     f'type or None. Actual type is {type(e)}.')
        
        if not isinstance(e, (_Element, XmlElement, TeiElement)):
            raise TypeError(error_msg)

        if isinstance(e, _Element):
            self._e = XmlElement(e)

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
    def create(
            cls, 
            localname: str, 
            attributes: dict[str, str] = dict()
        ) -> TeiElement:
        
        """
        Create a new Element in the TEI namespace with local name 
        `localname` and `attributes`
        """

        tag = ns.give_ns(localname, TEINS)
        elem = etree.Element(
            tag, 
            {k: v for k, v in attributes.items()}, 
            None
        )
        return TeiElement(elem)
    
    def get_attrib(
            self, 
            attribname: str, 
            namespace: str | None=None
        ) -> str | None:

        return self._e.get_attrib(attribname, namespace)
    
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
            lst=self.get_desc_tei_elems([elem_name], attribs=attribs),
            defaultval=None,
            throw_if_more_than_one=throw_if_more_than_one
        )

    def get_desc_tei_elems(
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
            for desc in self._e.get_desc(elem_names=elem_names, attribs=attribs)]
    
    def get_div_descendants(
            self, 
            divtype: str, 
            level: str = '',
            lang: str | None = None
        ) -> list[_Element]:

        if not lang:
            xpath_str = f".//ns:div{level}[@type='{divtype}']"
            return cast(list[_Element], self._e.xpath(xpath_str, namespaces={'ns': TEINS}))

        elif lang:
            return cast(list[_Element], self._e.xpath(
                f".//ns:div{level}[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': TEINS, 'xml': XMLNS}) 
            )
        
        return []
