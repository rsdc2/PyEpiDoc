from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.lxml_node_types import XmlElement
from pyepidoc.epidoc.representable import RepresentableElement


class Desc(RepresentableElement):
    def __init__(self, e: TeiElement | XmlElement):

        super().__init__(e)

        if self._e.localname != 'desc':
            raise TypeError(f'Element should be <corr> not {self._e.localname}.')
        
    @property
    def leiden_form(self):
        return f'[{self._e.text_desc}]'
    
    @property
    def normalized_form(self):
        return f'[{self._e.text_desc}]'

    @property
    def simple_lemmatized_edition_form(self) -> str:
        return f'{self._e.text_desc}'
    

    