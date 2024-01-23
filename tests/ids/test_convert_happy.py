from pyepidoc.epidoc.ids import convert, compress, ConversionError
from pyepidoc.epidoc.ids import validate
from pyepidoc.types import Base

import pytest


ids_to_convert = [
    ('AAAAA', 52, 100, 'AAAAA'),
    ('abcde', 52, 100, 'TnΤΕη'),
    ('zzzzz', 52, 100, 'mCAof'),
    ('mCAof', 100, 52, 'zzzzz')
]


@pytest.mark.parametrize(
        ['compressed_id', 
         'old_base', 
         'new_base', 
         'converted_id'], ids_to_convert)
def test_convert_ids_happy(
    compressed_id: str, 
    old_base: Base, 
    new_base: Base, 
    converted_id: str):
    
    assert convert(compressed_id, old_base, new_base) == converted_id
