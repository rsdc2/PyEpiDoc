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

SubsumableRels = [
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'c', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'Comment', 'ns': '', 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'lb', 'ns': TEINS, 'attrs': {'break': 'no'}}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'g', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'space', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'unclear', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'supplied', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'surplus', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'subst', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'link', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'del', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'hi', 'ns': TEINS, 'attrs': dict()}},
    {'head': {'name': 'w', 'ns': TEINS, 'attrs': dict()}, 'dep': {'name': 'choice', 'ns': TEINS, 'attrs': dict()}},
]
