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
    no_fixed_strs = remove_fixed_strs(uncompressed_id)
    required_length = 10 if base == 52 else 11
    valid = len(no_fixed_strs) == required_length

    if not valid:
        raise UncompressedIDLengthError(len(uncompressed_id), required_length)

    return valid