from pyepidoc.tei.s import S
from .ario_w import ArioW as W

class ArioS(S):
    
    @property
    def ws(self) -> list[W]:
        return [W(child) for child in self.children 
                if child.localname == 'w']