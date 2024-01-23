"""
Functions for validating IDs
"""
from typing import Literal
from .errors import *
from .format import *



def compressed_length(compressed_id: str) -> bool:
    """
    Checks that a compressed ID is of the correct length 
    (5 characters).
    If error is set to True, raises a CompressedIDLengthError
    """
    valid = len(compressed_id) == 5

    if not valid:
        raise CompressedIDLengthError(len(compressed_id))

    return valid


def uncompressed_length(uncompressed_id: str, base: Literal[52, 100]) -> bool:
    """
    Check that the length of an uncompressed id is correct for the base
    used
    """
    no_fixed_strs = remove_fixed_strs(uncompressed_id)
    required_length = 10 if base == 52 else 11
    valid = len(no_fixed_strs) == required_length

    if not valid:
        raise UncompressedIDLengthError(len(uncompressed_id), required_length)

    return valid


def max_int_size(uncompressed_id: str, base: Literal[52, 100]) -> bool:
    """
    Checks that the decimal integer of the element ID,
    e.g. ISic099999-99999, is below the integer limit for the
    respective base
    """
    no_fixed_strs = remove_fixed_strs(uncompressed_id)
    max_limit = 9999999999 if base == 100 else 380204031
    valid = int(no_fixed_strs) <= max_limit
    if not valid:
        raise IDSizeError(int(no_fixed_strs), max_limit)
    
    return valid


def max_int_token_part_size(
        uncompressed_id: str, 
        base: Literal[52, 100]) -> bool:

    token_part = uncompressed_id[:-5]
    
    if base == 52 and token_part[0] != '0':
        raise ConversionError(
            f'Token part {token_part} is too large'
        ) 

    return True