from typing import Optional
from os import getcwd, path, makedirs
from .filetypes import Path, FileMode
from .filename import Filename
from .funcs import filepath_from_list


class FileInfo(object):
    _full_folderpath: str
    _relative_folderpath: Optional[str]
    _filename: str

    def __init__(self, 
        filepath:str,
        mode=FileMode.r,
        create_folderpath:bool=True,
        fullpath=False
    ):
        if type(filepath) is not str:
            raise TypeError(f"filepath is of type {type(filepath)}, but should be of type str.")

        folderpath, filename = self.parse_filepath(filepath)
        self._filename = filename

        if fullpath:
            self._full_folderpath = folderpath
        else:
            self._relative_folderpath = folderpath
            self._full_folderpath = filepath_from_list([
                getcwd(),
                folderpath
            ])

        if mode == FileMode.r.value and not self.exists:
            raise FileExistsError(f'File {self.full_filepath} does not exist.')

        self._create_folderpath = create_folderpath

    def create_folderpath(self) -> None:
        if not path.exists(self.full_folderpath) and self._create_folderpath:
            makedirs(self.full_folderpath)

    @property
    def exists(self) -> bool:
        return path.exists(self.full_filepath)

    @property
    def full_filepath(self) -> str:
        filepath = filepath_from_list(
            [self.full_folderpath], 
            self._filename
        )
        return filepath

    @property
    def relative_filepath(self) -> Optional[Filename]:
        if self._relative_folderpath is not None:
            filepath = filepath_from_list([self._relative_folderpath], self._filename)
            return Filename(filepath)
        return None

    @property
    def filename(self) -> Filename:
        return Filename(self._filename)

    @property
    def full_folderpath(self) -> str:
        return self._full_folderpath

    def parse_filepath(self, fullpath:str) -> Path:
        items = fullpath.split('/')

        if len(items) == 1:
            return Path(None, items[0])

        folderpath = '/'.join(items[:-1])
        filename = items[-1]

        return Path(folderpath, filename)

    @property
    def relative_folderpath(self) -> Optional[str]:
        return self._relative_folderpath

    def __repr__(self):
        return self.full_filepath

    def __str__(self):
        return self.__repr__()