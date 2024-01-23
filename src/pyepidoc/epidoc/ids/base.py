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
