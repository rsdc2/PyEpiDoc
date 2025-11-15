from __future__ import annotations

from typing import Sequence, cast

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult

from pyepidoc.xml import XmlElement
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.shared.namespaces import TEINS, XMLNS

from pyepidoc.shared.iterables import maxone


class TeiElement(XmlElement):

    """
    Provides services to all TeiElement objects
    """

    def append_node(
            self, 
            item: _Element | _ElementUnicodeResult | str | XmlElement) -> TeiElement:

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

        elif isinstance(item, XmlElement):
            self.e.append(item.e)

        elif isinstance(item, _Element):
            self.e.append(item)

        else:
            raise TypeError(f'Expected: _Element or _ElementUnicodeResult; got {type(item)}')
        
        return self

    @property
    def child_elems(self) -> Sequence[TeiElement]:
        return [TeiElement(child) for child in self.child_elements]

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
    
    def get_descendant_tei_element(
            self, 
            elem_name: str, 
            attribs: dict[str, str] | None = None,
            throw_if_more_than_one: bool = False
        ) -> XmlElement | None:
        
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
        ) -> list[XmlElement]:
        
        """
        Get all the descendant elements within a particular
        set of names in the TEI namespace.

        :param elem_names: the local names of the elements wanted
        :param attribs: the attributes of the elements wanted
        """

        return [XmlElement(desc) 
            for desc in self.get_desc(elem_names=elem_names, attribs=attribs)]
    
    def get_div_descendants(
            self, 
            divtype: str, 
            level: str = '',
            lang: str | None = None
        ) -> list[_Element]:

        if self.e is None: 
            return []

        if not lang:
            xpath_str = f".//ns:div{level}[@type='{divtype}']"
            return cast(list[_Element], self.e.xpath(xpath_str, namespaces={'ns': TEINS}))

        elif lang:
            return cast(list[_Element], self.e.xpath(
                f".//ns:div{level}[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': TEINS, 'xml': XMLNS}) 
            )
        
        return []
