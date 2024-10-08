import pytest

from pyepidoc.epidoc.errors import EpiDocValidationError
from pyepidoc import EpiDoc

def test_validate_on_load():
    with pytest.raises(EpiDocValidationError) as err:
        _ = EpiDoc(
            'tests/xml/files/ISic000001_invalid.xml', 
            validate_on_load=True
        )
    assert ('196:0:ERROR:RELAXNGV:RELAXNG_ERR_CONTENTVALID: '
            'Element body failed to validate content') in str(err.value)