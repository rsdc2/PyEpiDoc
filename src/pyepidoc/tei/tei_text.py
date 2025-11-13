from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.body import Body
from pyepidoc.shared.iterables import maxone


class Text(TeiElement):

    @property
    def body(self) -> Body:
        self.child_elems
        body = self.child_element_by_local_name('body')
        if body is None:
            raise ValueError('No body element present.')
        return Body(body)