from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.tei_w import TeiW as W

class TeiS(TeiElement):
    @property
    def ws(self) -> list[W]:
        return [W(child) for child in self._e.child_elements 
                if child.localname == 'w']