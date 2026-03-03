from pyepidoc.xml.xml_node_types import XmlComment

def test_get_comment_text():
    # Arrange
    comment = XmlComment.from_str('This is a comment')

    # Act
    text = comment.text

    # Assert
    assert text == 'This is a comment'


def test_set_comment_text():
    # Arrange
    comment = XmlComment.from_str('This is a comment')

    # Act
    comment.text = 'This is an excellent comment'

    # Assert
    assert comment.text == 'This is an excellent comment'