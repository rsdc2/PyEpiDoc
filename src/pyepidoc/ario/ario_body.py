from pyepidoc.shared.iterables import maxone
from pyepidoc.tei.tei_body import TeiBody
from .ario_div1 import ArioDiv1 as Div1


class ArioBody(TeiBody):
    
    @property
    def discourse_body(self) -> Div1 | None:
        discourse_candidates = [div1 for div1 in self.div1s 
                                if div1.type == 'discourse'
                                and div1.subtype == 'body']
        discourse = maxone(discourse_candidates)
        if discourse is None: 
            return None
        return Div1(discourse)
