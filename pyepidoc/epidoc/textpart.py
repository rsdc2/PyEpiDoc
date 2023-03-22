from .constants import XMLNS
from ..xml.element import Element


class TextPart(Element):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    