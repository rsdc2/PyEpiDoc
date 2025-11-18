from pyepidoc.tei.tei_element import TeiElement

class TeiDiv1(TeiElement):
    
    @property
    def type(self) -> str | None:
        return self._e.get_attrib('type')
    
    @property
    def subtype(self) -> str | None:
        return self._e.get_attrib('subtype')