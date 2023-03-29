from typing import Optional
from os import getcwd, path, makedirs
from .filetypes import FilePath, FileMode
from .filename import Filename
from .funcs import filepath_from_list


class FileInfo(object):
    _full_folderpath: str
    _relative_folderpath: Optional[str]
    _filename: str

    def __init__(self, 
        filepath:str,
        mode=FileMode.r,
        create_folderpath:bool=False,
        fullpath:bool=False
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

        if mode == FileMode.r and not self.exists:
            raise FileExistsError(f'File {self.full_filepath} does not exist.')    

        self._create_folderpath = create_folderpath
        self._handle_create_folderpath()

    def _handle_create_folderpath(self) -> None:
        """
        Creates self.full_folderpath, including 
        all intermediate subdirectories, 
        if self._create_folderpath is set to True. 
        Raises |FileExistsError| if the folderpath
        does not exist and self._create_folderpath
        is set to False (default).
        """
        if not path.exists(self.full_folderpath):
            if self._create_folderpath:
                makedirs(self.full_folderpath, exist_ok=True)
            else:
                raise FileExistsError(
                    "The folder path does not exist. \
                        If you would like to create the folder path, \
                        please set the FileInfo create_folderpath variable \
                        to True."
                )

    @property
    def exists(self) -> bool:
        return path.exists(self.full_filepath)

    @property
    def full_filepath(self) -> str:
        """
        Returns the full path of the file.
        """

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

    def parse_filepath(self, fullpath:str) -> FilePath:
        items = fullpath.split('/')

        if len(items) == 1:
            return FilePath(None, items[0])

        folderpath = '/'.join(items[:-1])
        filename = items[-1]

        return FilePath(folderpath, filename)

    @property
    def relative_folderpath(self) -> Optional[str]:
        return self._relative_folderpath

    def __repr__(self):
        return self.full_filepath

    def __str__(self):
        return self.__repr__()