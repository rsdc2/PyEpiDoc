from itertools import chain

from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.tei_s import TeiS
from pyepidoc.tei.tei_w import TeiW

class TeiP(TeiElement):
    @property
    def ss(self) -> list[TeiS]:
        return [TeiS(child) for child in self._e.child_elements
                if child.tag.name == 's']
    
    @property
    def ario_text(self) -> str:
        return ' '.join((w.text for w in self.ws))

    @property
    def ws(self) -> list[TeiW]:
        return list(chain(*[s.ws for s in self.ss]))