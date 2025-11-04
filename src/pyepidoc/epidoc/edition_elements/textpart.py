from ...shared.constants import XMLNS
from ..edition_element import EditionElement


class TextPart(EditionElement):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    