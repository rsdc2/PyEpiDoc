from lxml.etree import _Element
from pyepidoc.epidoc.representable import Representable

class Desc(Representable):
    def __init__(self, e: _Element):
        if type(e) is not _Element:
            raise TypeError('e should be of type _Element.')

        self._e = e

        if self.localname != 'desc':
            raise TypeError('Element should be <desc>.')
        
    # @property
    # def simple_lemmatized_edition_form(self) -> str:
    #     return self.text_desc