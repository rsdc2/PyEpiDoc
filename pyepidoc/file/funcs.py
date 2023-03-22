from __future__ import annotations
from enum import Enum
from os import makedirs, path, getcwd
from typing import Union, Optional
from collections import namedtuple
from enum import Enum

from .filetypes import Path, FileMode


def filepath(folderpath:str, filename:str) -> str:
    if folderpath == '' or folderpath is None:
        return filename
    
    if folderpath[-1] != '/': folderpath += '/'
    return ''.join([folderpath, filename])


def filepath_from_list(
    folder_list:list, 
    filename:Optional[Union[str, list]]=None
) -> str:
    

    output_list:list = []

    for item in folder_list:
        if item == '' or item is None: 
            continue
        
        new_item = item

        if len(output_list) > 0:
            if output_list[-1][-1] == '/':
                output_list[-1] = output_list[-1][:-1]

        if new_item[0] != '/': new_item = '/' + new_item
        if new_item[-1] != '/': 
            new_item += '/'


        output_list += [new_item]
    
    if isinstance(filename, str):
        output_list += [filename]
    elif isinstance(filename, list):
        output_list += filename

    return ''.join(output_list)



