from __future__ import annotations
from typing import Optional, Union, Sequence, overload, cast, Literal
from functools import cached_property
import os

from .epidoc import EpiDoc
from .token import Token
from .expan import Expan
from .epidoc_types import SpaceUnit, TextClass
from pyepidoc.shared_types import SetRelation

from ..file import FileInfo, FileMode, filepath_from_list
from ..utils import maxone, flatlist, top, head, tail


class EpiDocCorpus:

    """
    Provides an interface for handling a corpus of 
    (i.e. more than one) EpiDoc files.
    """

    _docs: Optional[list[EpiDoc]]
    _head: Optional[int]
    _folderpath: Optional[str]

    # Optional because not all ways of initiating involve a file
    _fullpath: Optional[bool]

    def __add__(self, other:EpiDocCorpus) -> EpiDocCorpus:
        if not isinstance(other, EpiDocCorpus):
            raise TypeError("Cannot append: item to "
                            "be appended is of type "
                            f"{type(other)}; " 
                            "required: EpiDocCorpus")

        if self.fullpath != other.fullpath:
            if self.docs == []:
                return EpiDocCorpus(inpt=other.docs, folderpath=other.folderpath, fullpath=other.fullpath)
            elif other.docs == []:
                return EpiDocCorpus(inpt=self.docs, folderpath=self.folderpath, fullpath=self.fullpath)
            
            raise ValueError("Cannot resolve whether full path to corpus is given.")        

        return EpiDocCorpus(list(set(self.docs + other.docs)), fullpath=None)

    @overload
    def __init__(
        self,
        inpt: EpiDocCorpus,
        folderpath:Optional[str]=None,
        head:Optional[int]=None,
        fullpath:Optional[bool]=None
        ):

        """
        :param inpt: EpiDocCorpus object
        """
        ...

    @overload
    def __init__(
        self,
        inpt: list[EpiDoc],
        folderpath:Optional[str]=None,
        head:Optional[int]=None,
        fullpath:Optional[bool]=None
    ):
        """
        :param inpt: list of EpiDoc objects
        """
        ...

    @overload
    def __init__(
        self,
        inpt: str,
        folderpath:Optional[str]=None,
        head:Optional[int]=None,
        fullpath:Optional[bool]=None
    ):
        """
        :param inpt: path to the corpus
        """
        ...

    @overload
    def __init__(
        self,
        inpt: None,
        folderpath:Optional[str]=None,
        head:Optional[int]=None
    ):
        ...

    def __init__(
        self, 
        inpt: EpiDocCorpus | list[EpiDoc] | str | None, 
        folderpath:Optional[str]=None,
        head:Optional[int]=None
    ):
        
        self._docs = None  
        self._head = head
        self._fullpath 

        if type(inpt) is EpiDocCorpus:
            self._folderpath = inpt.folderpath
            self._docs = inpt.docs
            self._fullpath = inpt._fullpath
            return
        elif type(inpt) is list:
            self._folderpath = folderpath
            if inpt == []:
                return
            elif type(inpt[0]) is EpiDoc:
                self._docs = [doc for doc in inpt]
                return
        elif type(inpt) is str:

            # Check validity of the path to the corpus
            if fullpath is None:
                raise ValueError("Must specify whether a full path to corpus is given.")

            if self.fullpath:            
                if not os.path.isdir(inpt):
                    raise FileExistsError(f"Path {inpt} does not exist. Cannot create corpus")
            else:
                if not os.path.isdir(os.getcwd() + '/' + inpt)       :
                    raise FileExistsError(f"Path {os.getcwd() + '/' + inpt} does not exist. Cannot create corpus")
            
            if fullpath == True: 
                if os.name == 'nt' and len(inpt) > 3 and inpt[1:3] != ':\\':
                    raise ValueError('Fullpath specified, but path is not a path from root.')
                    
                elif os.name == 'posix' and len(inpt) > 0 and inpt[0] not in ['/']:
                        raise ValueError('Fullpath specified, but path is not a path from root.')                    
            
            self._folderpath = inpt
            return
            
        elif inpt is None:
            self._folderpath = folderpath
            return

        raise TypeError("Invalid input type.")
    
    def __repr__(self) -> str:
        return f'EpiDocCorpus( doc_count = {self.doc_count} )'

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
    def doc_count(self) -> int:
        """
        Returns the number of EpiDoc objects in the corpus.
        """
        return len(self.docs)

    @staticmethod
    def _doc_to_xml_file(dstfolder:Optional[str], doc:EpiDoc, fullpath:bool, create_folderpath:bool) -> None:
        
        "Writes out an EpiDoc object to an XML file"

        if dstfolder:
            dst = FileInfo(
                filepath = dstfolder + "/" + doc.id + ".xml", 
                mode=FileMode.w, 
                create_folderpath=create_folderpath,
                fullpath=fullpath
            )
            doc.to_xml_file(
                dst.full_filepath,
                fullpath=True
            )

    @cached_property
    def docs(self) -> list[EpiDoc]:
        if self._docs is None:
            print('Loading epidoc files...')
            self._docs = [EpiDoc(file) 
                for file in top(self.files, self._head)] 
        
        return self._docs

    def epidoc(self, filename:str) -> EpiDoc:
        if self.folderpath is None:
            filepath = filename
        else:
            filepath = filepath_from_list([self.folderpath], filename)
        
        file = FileInfo(
            filepath=filepath, 
            mode=FileMode.r
        )
        _epidoc = EpiDoc(file)
        return _epidoc

    @property
    def expans(self) -> list[Expan]:
        return flatlist([doc.expans for doc in self.docs])

    @cached_property
    def files(self) -> list[FileInfo]:

        """
        Returns a list of |FileInfo| for the files in the corpus.
        No subdirectories will be considered.
        """

        if self._folderpath is None:
            return []

        if self.fullpath is None:
            raise ValueError("Must specify whether full path to corpus is given.")

        l = list(os.walk(self._folderpath))
        
        if l == []:
            return []
        
        _, _, files = l[0] 
        sorted_files = sorted(files)

        fileinfos:list[FileInfo] = []
        
        for file in sorted_files:
            if file[-4:] == '.xml':
                if self.folderpath is None:
                    filepath = file
                else:
                    filepath = filepath_from_list([self.folderpath], file)

                fileinfos += [FileInfo(
                    filepath=filepath,
                    fullpath=self.fullpath
                )]

        return fileinfos

    def filter_by_dateafter(self, start:int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs
            if (doc.not_before is not None and doc.not_before >= start) 
            or (doc.date is not None and doc.date >= start)]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)        
        
        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_daterange(self, start:int, end:int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs
            if doc.not_before is not None and doc.not_after is not None
            and doc.not_before >= start and doc.not_after <= end]
        
        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_form(
        self, 
        forms:list[str], 
        set_relation=SetRelation.intersection
    ) -> EpiDocCorpus:
    
        docs = [doc for doc in self.docs
            if set_relation(set(forms), doc.forms)]
        
        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(
            inpt=docs, 
            folderpath=self.folderpath, 
            fullpath=self.fullpath)

    def filter_by_has_gap(
        self,
        has_gap=False,
        reasons:list[str]=[]
    ) -> EpiDocCorpus:
    
        docs = [doc for doc in self.docs
            if doc.has_gap(reasons=reasons) == has_gap]
        
        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_has_supplied(
        self,
        has_supplied=False
    ) -> EpiDocCorpus:
        
        """
        Filters the corpus
        according to whether or not it contains a <supplied>
        element.

        :param has_supplied: False returns a corpus where 
        no documents have a <supplied> element; True 
        returns a corpus where all the documents have a 
        <supplied> element.
        """
    
        docs = [doc for doc in self.docs
            if doc.has_supplied == has_supplied]
        
        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)
    
    def filter_by_idrange(self, start:int, end:int) -> EpiDocCorpus:
        _int_range = range(start, end + 1)
        _str_range = [self.prefix + str(item).zfill(6) for item in _int_range]
        
        return self.filter_by_ids(ids=_str_range)

    def filter_by_ids(self, ids:list[str]) -> EpiDocCorpus:
        docs = [doc for doc in self.docs
            if doc.id in ids]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_languages(self, 
        langs:list[str], 
        set_relation=SetRelation.intersection,
        language_attr:Literal['langs'] | Literal['div_langs']='langs'
    ) -> EpiDocCorpus:
        """
        Returns a copy of the corpus filtered by the 
        languages provided in the 'langs' parameter.
        Uses the 'textLang' element in the EpiDoc.
        """

        docs = [doc for doc in self.docs
            if set_relation(set(langs), doc.get_lang_attr(language_attr))]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)
        
        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_lemmata(
        self, 
        lemmata:list[str], 
        set_relation=SetRelation.intersection
    ) -> EpiDocCorpus:
    
        docs = [doc for doc in self.docs
            if set_relation(set(lemmata), doc.lemmata)]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=self.folderpath, fullpath=self.fullpath)

    def filter_by_orig_place(
        self,
        orig_places:list[str],
        set_relation=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        """
        Filters the corpus according to the value
        of <orig_place>.

        :param set_relation: a value of SetRelation
        """

        docs = [doc for doc in self.docs
            if set_relation(set(orig_places), set([doc.orig_place]))]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(docs, folderpath=None)

    def filter_by_textclass(
        self, 
        textclasses:list[str | TextClass], 
        set_relation=SetRelation.intersection
    ) -> EpiDocCorpus:

        # Convert input textclasses to their string representation
        _textclasses = list(map(str, textclasses))
    
        docs = [doc for doc in self.docs
            if set_relation(set(_textclasses), doc.textclasses)]

        if docs == []:
            return EpiDocCorpus([], folderpath=None, fullpath=None)  

        return EpiDocCorpus(
            inpt=docs, 
            folderpath=self.folderpath, 
            fullpath=self.fullpath)

    @property
    def folderpath(self) -> Optional[str]:
        return self._folderpath

    @property
    def formatted_text(self) -> str:
        return ''.join([doc.formatted_text for doc in self.docs])

    @property
    def fullpath(self) -> Optional[bool]:
        if self._folderpath is None:
            return None

        if os.name == 'nt' and len(self._folderpath) > 3 and self._folderpath[1:3] != ':\\':
            raise ValueError('Fullpath specified, but path is not a path from root.')
            
        elif os.name == 'posix' and len(self._folderpath) > 0 and self._folderpath[0] not in ['/']:
                raise ValueError('Fullpath specified, but path is not a path from root.')                    


    def get_doc_by_id(self, id:str) -> Optional[EpiDoc]:
        docs = self.filter_by_ids([id]).docs
        if docs == []:
            return None
        
        if len(docs) > 1:
            raise ValueError(f"More than one doc with id {id}.")
        
        return docs[0]

    @cached_property
    def ids(self) -> list[Optional[str]]:
        return [doc.id for doc in self.docs]

    @property
    def languages(self) -> set[str]:
        return set([lang for doc in self.docs 
                    for lang in doc.div_langs])

    def list_unique_orig_places(
        self,
        frequencies:bool=True,
        min_freq:int=0,
        sort_on:Optional[str]=None,
        reverse:bool=True
    ) -> Sequence[tuple[str, int] | str]:

        """
        Returns a list either of |tuple[str, int]| or of |str|
        giving the ancient sites of origin of the documents in
        the corpus.  
        The min_freq parameter is ignored if the frequencies parameter is False.
        """

        if sort_on not in ['place', 'freq', None]:
            raise ValueError(f'Cannot sort on {sort_on}.')

        places = [doc.orig_place for doc in self.docs]
        unique_places = set(places)

        if sort_on == 'place':
            places = sorted(unique_places, reverse=reverse)

        if frequencies:
            places_with_freq = [
                (
                    unique_place, 
                    len(list(filter(lambda doc: doc.orig_place==unique_place, self.docs)))
                ) 
                for unique_place in unique_places
            ]

            # Filter out those below minimum frequency
            places_with_freq = [x for x in places_with_freq if x[1] >= min_freq]
            
            if sort_on == 'freq':
                places_with_freq = sorted(
                    places_with_freq, 
                    key=lambda place_with_freq: place_with_freq[1], 
                    reverse=reverse
            )

                return places_with_freq

            return places_with_freq

        return places

    def multilinguals(self, head:Optional[int]=None) -> list[EpiDoc]:
        return [doc for doc in self.docs if doc.is_multilingual]

    @cached_property
    def prefix(self) -> str:
        doc = maxone(self.docs, None, throw_if_more_than_one=True)
        if doc is None:
            return ''
        
        return doc.prefix

    def set_ids(
            self, 
            dstfolder:str, 
            fullpath:bool, 
            verbose=True,
            create_folderpath:bool=False) -> None:
        for doc in self.docs:
            if verbose: print(f'Setting ids for {doc.id}...')
            doc.set_ids()
            self._doc_to_xml_file(
                dstfolder=dstfolder, 
                doc=doc, 
                fullpath=fullpath,
                create_folderpath=create_folderpath)

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

    def tokenize_to_folder(
        self, 
        dstfolder:str, 
        fullpath:bool,
        add_space_between_words:bool=True,
        prettify_edition:bool=True,
        set_ids:bool=False,
        convert_ws_to_names:bool=True,
        verbose:bool=True,
        create_folderpath:bool=False
    ) -> None:

        """
        Tokenizes the corpus and writes out the files 
        to dstfolder.
        """

        for doc in self.docs:
            if verbose: 
                print('Tokenizing', doc.id)

            doc.tokenize()
            
            if add_space_between_words:
                doc.space_tokens()
            
            if convert_ws_to_names:
                doc.convert_ws_to_names()

            if set_ids:
                doc.set_ids()
                
            if prettify_edition:
                doc.prettify_edition(spaceunit=SpaceUnit.Space, number=4)
            
            self._doc_to_xml_file(
                dstfolder, 
                doc, 
                fullpath=fullpath, 
                create_folderpath=create_folderpath
            )

    @property
    def token_count(self) -> int:
        return sum([doc.token_count for doc in self.docs])

    @property
    def tokens(self) -> list[Token]:
        return flatlist([doc.tokens for doc in self.docs])
    
    def top(self, length=10) -> EpiDocCorpus:
        return EpiDocCorpus(list(top(self.docs, length)))