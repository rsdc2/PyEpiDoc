from __future__ import annotations
from enum import Enum
from os import makedirs, path, getcwd
from typing import Union, Optional
from collections import namedtuple
from enum import Enum


class Filename(str):

    @property
    def subext(self):
        """
        Returns 'y.z' in a file such as x.y.z
        """
        return self._ext(self.base) + self.ext

    @staticmethod
    def _base(string:Union[Filename, str]) -> str:
        base, ext = path.splitext(string)
        return base

    @staticmethod
    def _ext(string:Union[Filename, str]) -> str:
        base, ext = path.splitext(string)
        return ext

    @property
    def base(self) -> str:
        return self._base(self)

    @property
    def ext(self) -> str:
        return self._ext(self)
    
    @property
    def noext(self) -> str:
        base, ext = path.splitext(self)
        return base

    def set_suff_ext(self, suffix:Optional[str] = None, ext:Optional[str] = None) -> str:
        def _add_suffix(suffix:Optional[str], filename:str) -> str:

            if suffix is None:
                return filename 

            base, ext = path.splitext(filename)
        
            return base + '_' + suffix + ext

        def _add_ext(new_ext:Optional[str], filename:str) -> str:
            if new_ext is None: return filename

            base, ext = path.splitext(filename)
            if ext == f'.{new_ext}':
                return filename

            return filename + f'.{new_ext}'

        return _add_ext(new_ext=ext, filename=_add_suffix(suffix=suffix, filename=self))

    @property
    def gv(self) -> str:
        return self.set_suff_ext(None, 'gv')

    @property
    def png(self) -> str:
        return self.set_suff_ext(None, 'png')

    @property
    def xml(self) -> str:
        return self.set_suff_ext(None, 'xml')
