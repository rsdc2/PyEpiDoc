from pyepidoc.tei.tei_element import TeiElement

class Text(TeiElement):

    @property
    def body(self):
        body_children = self.child_elements_by_local_name('body')