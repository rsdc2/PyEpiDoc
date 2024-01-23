"""
Functions for generating compressed token ids for I.Sicly documents. 
"""
from __future__ import annotations
from typing import Literal
from .errors import *
from .base import *
from .format import *
from . import validate
 

def compress(id: str, base: Literal[52, 100]) -> str:
    """
    Compresses an I.Sicily element ID 

    :param id: the element ID to generate
    :param base: the base to use in the generation of an ID 
    :returns: a compressed ID
    """
    _ = validate.uncompressed_length(id, base)
    _ = validate.max_size(id, base)

    zero = digits_dict[base][0]
    compressed = dec_to_base(int(remove_fixed_strs(id)), base)
    padded = compressed.rjust(5, zero)
    return padded


def decompress(compressed_id: str, base: Literal[52, 100]) -> str:
    """
    Decompresses an I.Sicily ID from base 'base' to base 10
    """

    _ = validate.compressed_length(compressed_id)

    decompressed = str(base_to_dec(compressed_id, base))
    _ = validate.max_size(decompressed, base)

    id_length = elem_id_length_from_base(base)
    return pad_and_insert_fixed_strs(decompressed, elem_id_length=id_length)


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
        decompressed = decompressed[0:7] + decompressed[8:]

    compressed = compress(decompressed, new_base)
    return compressed
