from pyepidoc.epidoc.ids import *

def test_id_correct_expansion():
    ID = 'ISic999999-9999'
    # ID = 'ISic000001-0010'
    b = 52
    x = compressId(ID, b)
    y = expandId(x, b)

    assert y == ID