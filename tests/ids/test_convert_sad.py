from pyepidoc.epidoc.ids import convert, compress, ConversionError
from pyepidoc.epidoc.ids import validate

import pytest


ids_to_convert = [
    ('abcde', 100, 52)
]


@pytest.mark.parametrize(['compressed_id', 'old_base', 'new_base'], ids_to_convert)
def test_convert_ids_sad(compressed_id, old_base, new_base):
    
    with pytest.raises(ConversionError):
        _ = convert(compressed_id, old_base, new_base)
