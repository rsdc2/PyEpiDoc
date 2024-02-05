from pyepidoc.utils.csv import pivot_dict

def test_pivot_dict():
    dict_dict = {'a': {'x': 1, 'y': 2, 'z': 3}, 'b': {'x': 10, 'y': 20, 'z': 30}}

    list_dict = pivot_dict(dict_dict)

    assert list_dict == [
        {'': 'a', 'x': 1, 'y': 2, 'z': 3},
        {'': 'b', 'x': 10, 'y': 20, 'z': 30}
    ]