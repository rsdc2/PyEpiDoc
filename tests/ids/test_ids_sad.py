from pyepidoc.epidoc.ids import *
from pyepidoc.epidoc.ids import validate
import pytest
from functools import partial


compressed_wrong_length_funcs = [
    validate.compressed_length,
    partial(decompress, base=52)
]


wrong_compressed_ids = [
    ('abcdef', 100)
]

@pytest.mark.parametrize('func', compressed_wrong_length_funcs)
def test_compressed_wrong_length(func):
    """
    Tests that a CompressedIDLengthError is raised when an 
    a compressed ID of the wrong length is generated
    """

    for (id, _) in wrong_compressed_ids:
        with pytest.raises(CompressedIDLengthError):
            func(compressed_id=id)


wrong_uncompressed_ids = [
    ('ISic000353-00305', 52),
    ('ISic000353-0001', 100)
]

@pytest.mark.parametrize(('id', 'base'), wrong_uncompressed_ids)
def test_uncompressed_wrong_length(id: str, base: Literal[52, 100]):
    """
    Tests that a CompressedIDLengthError is raised when an 
    a compressed ID of the wrong length is generated
    """

    with pytest.raises(UncompressedIDLengthError):
        _ = validate.uncompressed_length(id, base)


too_large_uncompressed_ids = [
    ('ISic099999-9999', 52),
    ('ISic199999-09999', 100)
]

@pytest.mark.parametrize(('id', 'base'), too_large_uncompressed_ids)
def test_too_large_uncompressed(id: str, base: Literal[52, 100]):
    with pytest.raises(IDSizeError):
        _ = validate.max_size(id, base)
