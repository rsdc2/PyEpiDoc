from pyepidoc.tei.p import P
from .ario_s import ArioS as S

class ArioP(P):
    
    @property
    def ss(self) -> list[S]:
        return [S(child) for child in self.child_elements
                if child.tag.name == 's']
