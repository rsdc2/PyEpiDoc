from lxml.etree import _ElementUnicodeResult

class XmlText:
    _text: _ElementUnicodeResult

    def __init__(self, text: _ElementUnicodeResult):
        self._text = text

    @property
    def text(self) -> str:
        return str(self._text)
    
    @property
    def localname(self) -> str:
        return "#text"

    @property
    def descendant_text(self) -> str:
        return str(self._text)
