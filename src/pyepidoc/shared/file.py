from __future__ import annotations
from enum import Enum
from collections import namedtuple
from pathlib import Path
import os

FilePath = namedtuple('FilePath', ['folderpath', 'filename'])


class FileMode(Enum):
    r = 'r'
    w = 'w'


def str_to_file(s: str, filepath: str):

    """
    Saves string s to file at path filepath.
    Raises FileExistsError if file already exists.
    """
    fp = Path(filepath)

    if fp.exists():
        raise FileExistsError(f'File already exists at path {filepath}.')

    with open(fp, mode='w') as f:
        f.write(s)


def remove_file(filepath: str):

    try:
        tokenized_f = Path(filepath)
        if tokenized_f.exists():
            os.remove(tokenized_f.absolute())

    except FileExistsError:
        pass