from __future__ import annotations
from typing import Union, Optional
from ..utils import remove_none

from .filetypes import FilePath, FileMode


def filepath(folderpath:str, filename:str) -> str:
    if folderpath == '' or folderpath is None:
        return filename
    
    if folderpath[-1] != '/': folderpath += '/'
    return ''.join([folderpath, filename])


def filepath_from_list(
    folder_list:list[str], 
    filename:Optional[Union[str, list]]=None
) -> str:

    # folder_list_with_no_none = remove_none(folder_list)
    output_str = '/'.join(folder_list)

    if output_str[-1] != '/':
        output_str += '/'
    
    if isinstance(filename, str):
        output_str += filename
    elif isinstance(filename, list):
        output_str += filename[0]

    return output_str



