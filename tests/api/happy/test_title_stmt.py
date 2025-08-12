from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.title_stmt import TitleStmt
from .test_epidoc_happy import relative_filepaths
from tests.config import EMPTY_TEMPLATE_PATH

def test_append_resp_stmt():

    # Arrange
    epidoc = EpiDoc(EMPTY_TEMPLATE_PATH)
    title_stmt = epidoc.title_stmt
    resp_stmt_count = len(title_stmt.resp_stmts)

    # Act
    title_stmt.append_new_resp_stmt("Robert Crellin", "RC", "xyz", "abc")
    new_resp_stmt_count = len(title_stmt.resp_stmts)
    
    # Assert
    assert new_resp_stmt_count == resp_stmt_count + 1


def test_does_not_append_resp_stmt_if_already_exists():

    # Arrange
    epidoc = EpiDoc(EMPTY_TEMPLATE_PATH)
    title_stmt = epidoc.title_stmt
    title_stmt.append_new_resp_stmt("Robert Crellin", "RC", "xyz", "abc")
    resp_stmt_count = len(title_stmt.resp_stmts)

    # Act
    title_stmt.append_new_resp_stmt("Robert Crellin", "RC", "xyz", "abc")
    new_resp_stmt_count = len(title_stmt.resp_stmts)

    # Assert
    assert new_resp_stmt_count == resp_stmt_count