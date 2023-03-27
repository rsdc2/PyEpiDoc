from __future__ import annotations
from typing import Optional, Union
from functools import reduce, cached_property
import os

from ..file import FileInfo, FileMode
from .epidoc import EpiDoc
from .epidoctypes import (
    SetRelation,
    TokenInfo, 
    AbbrInfo, 
    SpaceUnit
)

from ..file.funcs import filepath_from_list
from ..utils import maxone
from .constants import SET_IDS
from ..utils import head

class EpiDocCorpus:

    _docs: Optional[list[EpiDoc]]
    _head: Optional[int]
    _folderpath: Optional[str]
    _fullpath:bool

    def __init__(
        self, 
        input:Optional[Union[EpiDocCorpus, list[EpiDoc]]]=None, 
        folderpath:Optional[str]=None, 
        head:Optional[int]=None,
        fullpath=False
    ):

        self._docs = None  
        self._head = head
        self._fullpath = fullpath

        if type(input) is EpiDocCorpus:
            self._folderpath = input.folderpath
            self._docs = input.docs
            self._fullpath = input._fullpath
            return
        elif type(input) is list:
            self._folderpath = folderpath
            if input == []:
                return
            elif type(input[0]) is EpiDoc:
                self._docs = [doc for doc in input]
                return
        elif input is None:
            self._folderpath = folderpath
            return

        raise TypeError("Invalid input type.")

    @property
    def datemin(self) -> int:
        not_afters = [doc.not_after for doc in self.docs if doc.not_after is not None]
        dates = [doc.date for doc in self.docs if doc.date is not None]

        return min(not_afters + dates)

    @property
    def datemax(self) -> int:
        not_befores = [doc.not_before for doc in self.docs 
            if doc.not_after is not None and doc.not_before is not None]
        dates:list[int] = [doc.date for doc in self.docs 
            if doc.date is not None]

        return max(not_befores + dates)

    @property
    def dateranges(self) -> list[tuple[Optional[int], Optional[int]]]:
        return [doc.date_range for doc in self.docs]

    @property
    def datemean(self) -> Optional[int]:
        datemeans = [datemean for datemean in self.datemeans 
            if datemean is not None]

        if datemeans == []:
            return None

        return int(sum(datemeans) / len(datemeans))

    @property
    def datemeans(self) -> list[Optional[float]]:
        return [doc.date_mean for doc in self.docs]

    @property
    def doccount(self) -> int:
        return len(self.docs)

    @staticmethod
    def _doc_to_xml(dstfolder:Optional[str], doc:EpiDoc) -> None:
        if dstfolder:
            dst = FileInfo(
                filepath = dstfolder + "/" + doc.id + ".xml", 
                mode='w', 
                create_folderpath=True
            )
            doc.to_xml(
                dst.full_filepath,
                fullpath=True
            )

    @cached_property
    def docs(self) -> list[EpiDoc]:
        if self._docs is None:
            print('Loading epidoc files...')
            self._docs = [EpiDoc(file) 
                for file in head(self.files, self._head)] 
        
        return self._docs

    def epidoc(self, filename:str) -> EpiDoc:
        filepath = filepath_from_list([self.folderpath], filename)
        file = FileInfo(
            filepath=filepath, 
            mode=FileMode.r
        )
        _epidoc = EpiDoc(file)
        return _epidoc

    @cached_property
    def files(self) -> list[FileInfo]:
        if self._folderpath is None:
            return []

        folder, subfolder, files = next(os.walk(self._folderpath))
        sorted_files = sorted(files)

        fileinfos:list[FileInfo] = []
        for file in sorted_files:
            if file[-4:] == '.xml':
                filepath = filepath_from_list([self.folderpath], file)
                fileinfos += [FileInfo(
                    filepath=filepath,
                    fullpath=True
                )]

        return fileinfos

    def filter_by_abbr_info(
        self, 
        abbr_infos:list[AbbrInfo], 
        set_relation=SetRelation.intersection) -> EpiDocCorpus:
        
        _corpus = [doc for doc in self.docs
            if set_relation(set(abbr_infos), doc.abbr_infos)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_dateafter(self, start:int) -> EpiDocCorpus:
        return EpiDocCorpus([doc for doc in self.docs
            if (doc.not_before is not None and doc.not_before >= start) 
            or (doc.date is not None and doc.date >= start)], folderpath=self.folderpath)

    def filter_by_daterange(self, start:int, end:int) -> EpiDocCorpus:
        return EpiDocCorpus([doc for doc in self.docs
            if doc.not_before is not None and doc.not_after is not None
            and doc.not_before >= start and doc.not_after <= end], folderpath=self.folderpath)

    def filter_by_form(self, forms:list[str], set_relation=SetRelation.intersection) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if set_relation(set(forms), doc.forms)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_ids(self, ids:list[str]) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if doc.id in ids]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_idrange(self, start:int, end:int) -> EpiDocCorpus:
        _int_range = range(start, end + 1)
        _str_range = [self.prefix + str(item).zfill(6) for item in _int_range]
        
        return self.filter_by_ids(ids=_str_range)

    def filter_by_languages(self, 
        languages:list[str], 
        set_relation=SetRelation.intersection) -> EpiDocCorpus:

        _corpus = [doc for doc in self.docs
            if set_relation(set(languages), doc.textlangs)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_lemmata(self, lemmata:list[str], set_relation=SetRelation.intersection) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if set_relation(set(lemmata), doc.lemmata)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_morphology(self, morphologies:list[TokenInfo], set_relation=SetRelation.intersection) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if set_relation(set(morphologies), doc.morphologies)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_textclass(self, textclasses:list[str], set_relation=SetRelation.intersection) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if set_relation(set(textclasses), doc.textclasses)]

        return EpiDocCorpus(_corpus, folderpath=None)

    def filter_by_word_info(self, word_infos:list[TokenInfo], set_relation=SetRelation.intersection) -> EpiDocCorpus:
        _corpus = [doc for doc in self.docs
            if set_relation(set(word_infos), doc.token_infos)]

        return EpiDocCorpus(_corpus, folderpath=None)

    @property
    def folderpath(self) -> Optional[str]:
        return self._folderpath

    @property
    def formatted_text(self) -> str:
        return ''.join([doc.formatted_text for doc in self.docs])

    @property
    def fullpath(self) -> bool:
        return self._fullpath

    @cached_property
    def ids(self) -> list[Optional[str]]:
        return [doc.id for doc in self.docs]

    @property
    def languages(self) -> set[str]:
        return set([lang for doc in self.docs for lang in doc.div_langs])

    def multilinguals(self, head:Optional[int]=None) -> list[EpiDoc]:
        return [doc for doc in self.docs if doc.ismultilingual]

    @cached_property
    def prefix(self) -> str:
        doc = maxone(self.docs, None, suppress_more_than_one_error=True)
        if doc is None:
            return ''
        
        return doc.prefix

    def set_uuids(self, dstfolder:Optional[str], verbose=True) -> None:
        if SET_IDS:
            if dstfolder is None: 
                return
            for doc in self.docs:
                if verbose: print(f'Setting ids for {doc.id}...')
                doc.set_uuids()
                self._doc_to_xml(dstfolder=dstfolder, doc=doc)

    @cached_property
    def size(self) -> int:
        return len(self.docs)

    @cached_property
    def textclasses(self) -> set[str]:
        return set([textclass for doc in self.docs for textclass in doc.textclasses])

    def to_txt(self, dst:FileInfo) -> None:
        """
        Writes a .txt file with the text of the documents
        in the corpus.
        """
        with open(dst.full_filepath, 'w') as f:
            f.write(self.formatted_text)

    def tokenize(self, dstfolder:Optional[str]=None, verbose=True) -> None:
        if dstfolder is None: 
            return

        for doc in self.docs:
            if verbose: 
                print('Tokenizing', doc.id)

            doc.tokenize()
            doc.add_space_between_tokens()
            
            if SET_IDS:
                doc.set_ids()
                
            doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)
            self._doc_to_xml(dstfolder=dstfolder, doc=doc)

    @property
    def tokencount(self) -> int:
        return sum([doc.tokencount for doc in self.docs])
