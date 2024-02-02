
from lxml.etree import XMLSyntaxError


def handle_xmlsyntaxerror(e: XMLSyntaxError):
    # print(
    #     f'XMLSyntaxError in {e.filename} '
    #     f'at line {e.lineno}, offset {e.offset}, position {e.position}'
    # )
    print(e)