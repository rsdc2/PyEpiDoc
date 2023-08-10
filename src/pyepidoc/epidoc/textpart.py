from ..constants import XMLNS
from .element import EpiDocElement


class TextPart(EpiDocElement):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    