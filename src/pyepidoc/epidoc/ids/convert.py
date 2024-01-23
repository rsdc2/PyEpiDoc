from typing import Literal
from .format import remove_fixed_strs
from .compress import compress, decompress
from .errors import ConversionError
from . import validate


def convert(
        old_id: str, 
        old_base: Literal[52, 100], 
        new_base: Literal[52, 100]) -> str:
    """
    Convert compressed ids between base 52 and base 100
    """

    decompressed = remove_fixed_strs(decompress(old_id, old_base))
    if old_base == 52:
        decompressed = decompressed[0:7] + '0' + decompressed[7:]
    elif old_base == 100:
        _ = validate.max_int_token_part_size(decompressed, 52)
        decompressed = decompressed[0:7] + decompressed[8:]

    compressed = compress(decompressed, new_base)
    return compressed