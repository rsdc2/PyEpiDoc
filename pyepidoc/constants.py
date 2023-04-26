NS = "http://www.tei-c.org/ns/1.0"
XMLNS = "http://www.w3.org/XML/1998/namespace"

NE = NAMED_ENTITIES = {'g', 'w', 'name', 'persName', 'num', 'roleName', 'orgName', 'placeName', 'measure'}
NE_TEXT = NAMED_ENTITIES_CONTAINING_TEXT = {'g', 'w', 'name', 'num', 'measure'}
NE_G = {'g'}
NE_NO_G = NAMED_ENTITIES_NO_G = NAMED_ENTITIES - {'g'}
NONWORDS = {'orig', 'gap', 'space'}

PUNCT = {'⁞', '⁝', '∶', '·', '.', ','}

LEFT_BRACE:str = '\u007b'
RIGHT_BRACE:str = '\u007d'

WHITESPACE:list = [' ', '\n']
WHITESPACE_RE = r'(\s+)'

VERBOSE = False

NS = "http://www.tei-c.org/ns/1.0"
XMLNS = "http://www.w3.org/XML/1998/namespace"

SubsumableRels = [
    {'head': {'name': 'w', 'ns': NS, 'attrs': dict()}, 'dep': {'name': 'lb', 'ns': NS, 'attrs': {'break': 'no'}}},
    {'head': {'name': 'w', 'ns': NS, 'attrs': dict()}, 'dep': {'name': 'g', 'ns': NS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': NS, 'attrs': dict()}, 'dep': {'name': 'space', 'ns': NS, 'attrs': dict()}},
]

SET_IDS = False
SPACE_WORDS = False