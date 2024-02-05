from pyepidoc.shared import flatlist
import pytest

list2D = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
list3D = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9]]]
lists = [list2D, list3D]
flat = [1, 2, 3, 4, 5, 6, 7, 8, 9]


@pytest.mark.parametrize("l", lists)
def test_flatlist(l:list):
    assert flatlist(l) == flat