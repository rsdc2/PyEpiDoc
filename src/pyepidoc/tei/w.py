from pyepidoc.shared.namespaces import XMLNS
from .tei_element import TeiElement

class TeiW(TeiElement):

    @property
    def form(self) -> str:
        return self.text
    
    @property
    def lemma(self) -> str | None:
        return self.get_attrib('lemma')
    
    @property
    def xmlid(self) -> str | None:
        return self.get_attrib('id', XMLNS)