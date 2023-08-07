from __future__ import annotations
from enum import Enum
from collections import namedtuple


FilePath = namedtuple('FilePath', ['folderpath', 'filename'])


class FileMode(Enum):
    r = 'r'
    w = 'w'