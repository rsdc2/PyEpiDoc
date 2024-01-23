"""
Functions for generating compressed token ids for I.Sicly documents. 
For algorithms, cf. https://en.wikipedia.org/wiki/Positional_notation#Base_conversion, last accessed 2023-07-05
I also found these articles helpful: https://iq.opengenus.org/convert-decimal-to-hexadecimal/, 
https://stackoverflow.com/questions/6692183/python-integer-to-base-32-hex-aka-triacontakaidecimal last accessed 2023-11-14
"""
from __future__ import annotations
from typing import Literal

UPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
LOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

LCASEGREEK1 = list('βδζηθλμνξπστφχψ')
UCASEGREEK1 = list('ΓΔΘΛΞΠΣΦΨΩ')
LCASEGREEK2 = list('αβγδεζηθικλμνξοπρστυφχψω')
UCASEGREEK2 = list('ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ')

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
digits52 = UPPERCASE + LOWERCASE
digits62 = DIGITS + digits52
digits87 = DIGITS + UPPERCASE + LOWERCASE + UCASEGREEK1 + LCASEGREEK1
digits77 = UPPERCASE + LOWERCASE + UCASEGREEK1 + LCASEGREEK1
digits100 = UPPERCASE + LOWERCASE + UCASEGREEK2 + LCASEGREEK2

digits_dict = {52: {k: v for (k, v) in enumerate(digits52)}, 
               62: {k: v for (k, v) in enumerate(digits62)},
               87: {k: v for (k, v) in enumerate(digits87)},
               77: {k: v for (k, v) in enumerate(digits77)},
               100: {k: v for (k, v) in enumerate(digits100)}}


def rev_digits(d: dict[int, str]) -> dict[str, int]:
    """
    Reverses a dictionary of digits to decimal equivalents
    """

    return {v: k for k, v in d.items()}


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


def dec_to_base(dec: int, base: Literal[52, 100]) -> str:
    """
    Convert a decimal number to a number of base 'base'.
    This works by recursively dividing the quotient by
    the base, to produce a quotient and a remainder, until 
    the quotient is less than the base. Each sequence 
    of quotient and remainder corresponds to two positions
    in the new base number.
    """

    def f(i: int) -> list[int]:
        q = i // base
        r = i % base

        return ([q] if q < base else f(q)) + [r]
        
    l = f(dec)
    return ''.join([digits_dict[base][item] for item in l])


def base_to_dec(base_inpt: str, base: Literal[52, 100]) -> int:
    
    """Convert a string of base 'base' to a base 10 integer"""
    
    def f(l: list[str], acc: int) -> int:
        if l == []:
            return acc
        
        v = rev_digits(digits_dict[base])[l[0]] * base ** (len(l) - 1)

        return f(l[1:], acc + v)
    
    return f(list(base_inpt), 0)
 

def compress(id: str, base: Literal[52, 100]) -> str:
    """
    Compresses an I.Sicily element ID 

    :param id: the element ID to generate
    :param base: the base to use in the generation of an ID 
    :returns: a compressed ID
    """
    zero = digits_dict[base][0]
    return dec_to_base(int(remove_fixed_strs(id)), base).rjust(5, zero)


def decompress(id: str, base: Literal[52, 100]) -> str:
    """
    Decompresses an I.Sicily ID from base 'base' to base 10
    """
    expanded = str(base_to_dec(id, base))
    id_length = elem_id_length_from_base(base)
    return pad_and_insert_fixed_strs(expanded, elem_id_length=id_length)


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



if __name__ == '__main__':
    x = decompress('ω', 100)
    # x = compress('')
    print(x)
