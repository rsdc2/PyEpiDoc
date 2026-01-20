from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement

from .pers_name import PersName

class PlaceName(PersName):

    def __init__(self, e: XmlElement | TeiElement):
        super().__init__(e)

        if self._e.localname != 'placeName':
            raise TypeError('Element should be <placeName>.')