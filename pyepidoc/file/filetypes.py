from __future__ import annotations
from enum import Enum
from os import makedirs, path, getcwd
from typing import Union, Optional
from collections import namedtuple
from enum import Enum

Path = namedtuple('Path', ['folderpath', 'filename'])


class FileMode(Enum):
    r = 'r'
    w = 'w'