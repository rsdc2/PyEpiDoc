from __future__ import annotations
from pathlib import Path


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