from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.title_stmt import TitleStmt
from .test_epidoc_happy import relative_filepaths

def test_append_resp_stmt():

    # Arrange
    epidoc = EpiDoc(relative_filepaths['ISic000001'])
    title_stmt = epidoc.title_stmt
    resp_stmt_count = len(title_stmt.resp_stmts)

    # Act
    title_stmt.append_new_resp_stmt("Robert Crellin", "RC", "xyz", "abc")
    new_resp_stmt_count = len(title_stmt.resp_stmts)
    
    # Assert
    assert new_resp_stmt_count == resp_stmt_count + 1