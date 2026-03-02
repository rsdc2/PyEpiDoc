
from lxml.etree import XMLSyntaxError, XMLSyntaxAssertionError


class PyEpiDocXmlSyntaxError(Exception):
    _inner_exception: XMLSyntaxError
    def __init__(self, message: str, inner_exception: XMLSyntaxError):
        super().__init__(message)
        self._inner_exception = inner_exception


class PyEpiDocXmlSyntaxAssertionError(Exception):
    _inner_exception: XMLSyntaxAssertionError
    def __init__(self, message: str, inner_exception: XMLSyntaxAssertionError):
        super().__init__(message)
        self._inner_exception = inner_exception


def handle_xmlsyntaxerror(e: XMLSyntaxError):
    # print(
    #     f'XMLSyntaxError in {e.filename} '
    #     f'at line {e.lineno}, offset {e.offset}, position {e.position}'
    # )
    print(e)

