from __future__ import annotations

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult

from pyepidoc.xml import XmlElement
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.shared.constants import TEINS


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

    @classmethod
    def create_new(cls, localname: str, attributes: dict[str, str] = dict()) -> TeiElement:
        """
        Create a new Element in the TEI namespace with local name `localname` and `attributes`
        """

        tag = ns.give_ns(localname, TEINS)
        elem = etree.Element(
            tag, 
            {k: v for k, v in attributes.items()}, 
            None
        )
        return TeiElement(elem)