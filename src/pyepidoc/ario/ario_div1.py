from pyepidoc.tei.tei_div1 import TeiDiv1
from pyepidoc.ario.ario_p import ArioP as P


class ArioDiv1(TeiDiv1):

    @property
    def ps(self) -> list[P]:
        return [P(child) for child in self.child_elements
                if child.tag.name == 'p']
