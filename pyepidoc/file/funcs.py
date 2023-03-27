from __future__ import annotations
from enum import Enum
from os import makedirs, path, getcwd
from typing import Union, Optional
from collections import namedtuple
from enum import Enum

from .filetypes import FilePath, FileMode


def filepath(folderpath:str, filename:str) -> str:
    if folderpath == '' or folderpath is None:
        return filename
    
    if folderpath[-1] != '/': folderpath += '/'
    return ''.join([folderpath, filename])


def filepath_from_list(
    folder_list:list, 
    filename:Optional[Union[str, list]]=None
) -> str:
    
    output_str = '/'.join(folder_list)
    if output_str[-1] != '/':
        output_str += '/'
    
    if isinstance(filename, str):
        output_str += filename
    elif isinstance(filename, list):
        output_str += filename[0]

    return output_str



