from ..constants import XMLNS
from .element import Element


class TextPart(Element):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    