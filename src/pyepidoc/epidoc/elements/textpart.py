from ...shared.constants import XMLNS
from ..epidoc_element import EpiDocElement


class TextPart(EpiDocElement):

    @property
    def lang(self):
        return self.get_attrib('lang', XMLNS)
    