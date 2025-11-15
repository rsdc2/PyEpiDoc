from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.epidoc.edition_element import EditionElement


class TextPart(EditionElement):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    