from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.tei_body import TeiBody
from pyepidoc.shared.iterables import maxone


class Text(TeiElement):

    @property
    def body(self) -> TeiBody:
        self.child_elems
        body = self._e.child_element_by_local_name('body')
        if body is None:
            raise ValueError('No body element present.')
        return TeiBody(body)