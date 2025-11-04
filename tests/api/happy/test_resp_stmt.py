from lxml.etree import _Element
from pyepidoc import EpiDoc
from pyepidoc.tei.metadata.resp_stmt import RespStmt


def test_create_resp_stmt():

    # Arrange 

    # Act
    resp_stmt = RespStmt.from_details("Resp Stmt", "RS", "xyz", "abc")
    resp_stmt_xml = resp_stmt.xml_byte_str

    # Assert
    assert resp_stmt_xml == b'<ns0:respStmt xmlns:ns0="http://www.tei-c.org/ns/1.0">\n  <ns0:name xml:id="RS" ref="xyz">Resp Stmt</ns0:name>\n  <ns0:resp>abc</ns0:resp>\n</ns0:respStmt>\n'

