from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.tei.tei_element import TeiElement
from .w import W


class Measure(W):

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'measure':
            raise TypeError(f'Element should be <w> not {self._e.localname}.')