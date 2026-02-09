from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.epidoc.tokenizable_element import TokenizableElement


class TextPart(TokenizableElement):

    @property
    def lang(self):
        return self.get_attr('lang', XMLNS)
    