"""
Functions for generating compressed token ids for I.Sicly documents. 
For algorithms, cf. https://en.wikipedia.org/wiki/Positional_notation#Base_conversion, last accessed 2023-07-05
I also found these articles helpful: https://iq.opengenus.org/convert-decimal-to-hexadecimal/, 
https://stackoverflow.com/questions/6692183/python-integer-to-base-32-hex-aka-triacontakaidecimal last accessed 2023-07-05
"""

UPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
LOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

digits52_list = UPPERCASE + LOWERCASE

digitsDict = {k: v for (k, v) in enumerate(digits52_list)}


def rev_digits(d:dict[int, str]) -> dict[str, int]:
    """
    Reverses a dictionary of digits to decimal equivalents
    """

    return {v: k for k, v in d.items()}


def remove_fixed_strs(id:str) -> int:
    """
    Strips ISic and '-' from an I.Sicily token ID
    """

    return int(id.replace('-', '').replace('ISic', ''))


def insert_fixed_strs(id:str) -> str:
    """
    Insert ISic and '-' for an I.Sicily token ID 
    """
    padded = id.rjust(10, '0')
    return 'ISic' + padded[:-4] + '-' + padded[-4:]


def dec_to_base(dec:int, base:int) -> str:
    """
    Convert a decimal number to a number of base 'base'.
    This works by recursively dividing the quotient by
    the base, to produce a quotient and a remainder, until 
    the quotient is less than the base. Each sequence 
    of quotient and remainder corresponds to two positions
    in the new base number.
    """

    def f(i:int) -> list[int]:
        q = i // base
        r = i % base

        return ([q] if q < base else f(q)) + [r]
        
    l = f(dec)
    return ''.join([digitsDict[item] for item in l])


def base_to_dec(baseInpt:str, base:int) -> int:
    
    """Convert a string of base 'base' to a base 10 integer"""
    
    def f(l:list[str], acc:int) -> int:
        if l == []:
            return acc
        
        v = rev_digits(digitsDict)[l[0]] * base ** (len(l) - 1)

        return f(l[1:], acc + v)
    
    return f(list(baseInpt), 0)


def compress(id:str, base:int) -> str:
    """Compresses an I.Sicily ID to base 'base'"""
    return dec_to_base(remove_fixed_strs(id), base).rjust(5, 'A')


def decompress(id:str, base:int) -> str:
    """Decompresses an I.Sicily ID from base 'base' to base 10"""
    expanded = str(base_to_dec(id, base))
    return insert_fixed_strs(expanded)
