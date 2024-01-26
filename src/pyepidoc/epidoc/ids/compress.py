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
    _ = validate.max_int_size(id, base)

    zero = digits_dict[base][0]
    no_fixed_strs = remove_fixed_strs(id)
    compressed = dec_to_base(int(no_fixed_strs), base)
    padded = compressed.rjust(5, zero)
    return padded


def decompress(compressed_id: str, base: Literal[52, 100]) -> str:
    """
    Decompresses a compressed 5-character I.Sicily element ID, 
    e.g. 'abcde'

    :param compressed_id: the compressed id to be decompressed, 
    e.g. 'abcde'
    :param base: the base to use to decompress the ID
    :returns: a string with the decompressed ID
    """
    _ = validate.compressed_length(compressed_id)

    decompressed = str(base_to_dec(compressed_id, base))
    _ = validate.max_int_size(decompressed, base)

    id_length = elem_id_length_from_base(base)
    return pad_and_insert_fixed_strs(decompressed, elem_id_length=id_length)

