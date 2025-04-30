TEINS = "http://www.tei-c.org/ns/1.0"
XMLNS = "http://www.w3.org/XML/1998/namespace"

NE = NAMED_ENTITIES = {'g', 'w', 'name', 'persName', 'num', 'roleName', 'orgName', 'placeName', 'measure'}
NE_TEXT = NAMED_ENTITIES_CONTAINING_TEXT = {'g', 'w', 'name', 'num', 'measure'}
NE_G = {'g'}
NE_NO_G = NAMED_ENTITIES_NO_G = NAMED_ENTITIES - {'g'}
NONWORDS = {'orig', 'gap', 'space'}

PUNCT = {'⁞', '⁝', '∶', '·', '.', ','}
A_TO_Z_SET = set('abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper())

LEFT_BRACE:str = '\u007b'
RIGHT_BRACE:str = '\u007d'

WHITESPACE:list = [' ', '\n']
WHITESPACE_RE = r'(\s+)'

ROMAN_NUMERAL_CHARS = {'I', 'V', 'X', 'C', 'D'}

VALID_BASES = [52, 100]
SEPARATE_LEMMATIZED_CONTAINER_ITEMS = ['div', 'ab']
SEPARATE_LEMMATIZED_TEXT_ITEMS = ['w', 'orig', 'gap']
SEPARATE_LEMMATIZED_ITEMS = SEPARATE_LEMMATIZED_CONTAINER_ITEMS + SEPARATE_LEMMATIZED_TEXT_ITEMS