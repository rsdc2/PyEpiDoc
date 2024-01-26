"""
For algorithms, cf. https://en.wikipedia.org/wiki/Positional_notation#Base_conversion, last accessed 2023-07-05
I also found these articles helpful: https://iq.opengenus.org/convert-decimal-to-hexadecimal/, 
https://stackoverflow.com/questions/6692183/python-integer-to-base-32-hex-aka-triacontakaidecimal last accessed 2023-11-14
"""

from typing import Literal

UPPERCASE = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
LOWERCASE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

LCASEGREEK1 = list('βδζηθλμνξπστφχψ')
UCASEGREEK1 = list('ΓΔΘΛΞΠΣΦΨΩ')
LCASEGREEK2 = list('αβγδεζηθικλμνξοπρστυφχψω')
UCASEGREEK2 = list('ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ')

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
digits52 = UPPERCASE + LOWERCASE
# digits62 = DIGITS + digits52
# digits87 = DIGITS + UPPERCASE + LOWERCASE + UCASEGREEK1 + LCASEGREEK1
# digits77 = UPPERCASE + LOWERCASE + UCASEGREEK1 + LCASEGREEK1
digits100 = UPPERCASE + LOWERCASE + UCASEGREEK2 + LCASEGREEK2

# Use a dict to store the information so that can easily reverse
digits_dict = {52: {k: v for (k, v) in enumerate(digits52)}, 
            #    62: {k: v for (k, v) in enumerate(digits62)},
            #    87: {k: v for (k, v) in enumerate(digits87)},
            #    77: {k: v for (k, v) in enumerate(digits77)},
               100: {k: v for (k, v) in enumerate(digits100)}}


def rev_digits(d: dict[int, str]) -> dict[str, int]:
    """
    Reverses a dictionary of digits to decimal equivalents
    """

    return {v: k for k, v in d.items()}


def dec_to_base(dec: int, base_idx: Literal[52, 100]) -> str:
    """
    Convert a decimal number to a number of base 'base'.
    This works by recursively dividing the quotient by
    the base, to produce a quotient and a remainder, until 
    the quotient is less than the base. Each sequence 
    of quotient and remainder corresponds to two positions
    in the new base number.
    """

    base_values = digits_dict[base_idx]

    def f(i: int) -> list[int]:
        # Get the quotient, i.e. the whole number of times
        # that the base goes into the integer
        q = i // base_idx 

        # Get the remainder, i.e. what is left over after
        # dividing i by dividing by the base index
        r = i % base_idx

        if q < base_idx:
            # The quotient is less than the base index,
            # so return the quotient and the remainder 
            # in two separate positions:
            # the first position constitutes 
            # the first power of the base index,
            # while the second position consitiutes
            # the zeroth power of the base index.
            
            return [q, r]
        else:
            return f(q) + [r]
    
    # Produce a list of decimal values 
    # each corresponding to a value in the new base.
    # This value can be looked up in the 
    # list providing all the values of the base
    # indexed by decimal value
    l = f(dec)

    # Look up all the items and concatenate the strings
    return ''.join([base_values[base_value] for base_value in l])


def base_to_dec(base_inpt: str, base: Literal[52, 100]) -> int:
    
    """
    Convert a string of base 'base' to a base 10 integer
    """

    base_values = rev_digits(digits_dict[base])
    
    def f(l: list[str], acc: int) -> int:
        """
        :param l: a list of characters giving the value in
        the base
        :param acc: an accumulator that takes the running
        sum of the base conversion calculation
        """
        # No more digits to convert
        if l == []:
            return acc
        
        # Each position in the string from the left
        # corresponds to a power of the base index,
        # where the right-most digit is power 0, i.e. 1.
        # This constitutes the multiplier for the value 
        # at this position

        multiplier = base ** (len(l) - 1)
        v = base_values[l[0]] * multiplier
        return f(l[1:], acc + v)
    
    # Calculate the value of the base
    # starting from the left-most digit
    return f(list(base_inpt), 0)

