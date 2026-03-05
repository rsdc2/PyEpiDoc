from .characters import character_map, interpunct


def string_to_op(roman: str) -> str:
    """
    Transliterate a Roman-transliterated string to Old Persian cuneiform.
    Words are separated by the word divider.
    """

    words = roman.split(' ')
    op = [word_to_op(word) for word in words]
    return interpunct.join(op)


def word_to_op(roman: str) -> str:
    """
    Transliterate a Roman-transliterated string to Old Persian cuneiform
    """
    chars = roman.split('-')
    filtered = [char for char in chars if char != '']
    op = [character_map.get(char, f'["{char}" not found]') for char in filtered]
    return ''.join(op)


