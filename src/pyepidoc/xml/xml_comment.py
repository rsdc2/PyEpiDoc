from lxml.etree import _Comment

class XmlComment:

    _comment: _Comment

    def __init__(self, comment: _Comment):
        self._comment = comment

    @property
    def text(self) -> str:
        return str(self._comment)
    
    @property
    def localname(self) -> str:
        return "#comment"