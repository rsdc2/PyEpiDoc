from .pers_name import PersName
from lxml.etree import _Element

class PlaceName(PersName):

    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self._e.localname != 'placeName':
            raise TypeError('Element should be <placeName>.')