from typing import Literal


def remove_fixed_strs(id: str) -> str:
    """
    Strips ISic and '-' from an I.Sicily token ID
    """
    result = id.replace('-', '').replace('ISic', '')
    return result


def elem_id_length_from_base(base: Literal[52, 100]) -> Literal[4, 5]:
    if base == 52: 
        return 4
    
    if base == 100:
        return 5


def pad_and_insert_fixed_strs(id: str, elem_id_length: Literal[4, 5]) -> str:
    """
    Pad and insert ISic and '-' for an I.Sicily token ID 
    """
    if elem_id_length == 4:
        padded = id.rjust(10, '0')
    elif elem_id_length == 5:
        padded = id.rjust(11, '0')

    return 'ISic' + padded[:-elem_id_length] + '-' + padded[-elem_id_length:]
