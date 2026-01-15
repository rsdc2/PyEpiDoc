from pyepidoc.shared.namespaces import XMLNS
from .tei_element import TeiElement

class TeiW(TeiElement):

    @property
    def form(self) -> str:
        return self._e.text
    
    @property
    def lemma(self) -> str | None:
        return self.get_attr('lemma')
    
    @property
    def xmlid(self) -> str | None:
        return self.get_attr('id', XMLNS)