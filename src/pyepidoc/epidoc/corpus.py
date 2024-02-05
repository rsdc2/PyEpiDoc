from __future__ import annotations
from typing import (
    Callable,
    Optional, 
    Sequence, 
    overload, 
    cast, 
    Literal, 
    Generator
)
from functools import cached_property
from itertools import chain
from pathlib import Path

from lxml.etree import (
    XMLSyntaxAssertionError, 
    XMLSyntaxError
)  

from .epidoc import EpiDoc
from .element import EpiDocElement
from .token import Token
from .elements.expan import Expan
from .enums import TextClass
from pyepidoc.shared.classes import SetRelation

from ..shared import maxone, top


class EpiDocCorpus:

    """
    Provides an interface for handling a corpus of 
    (i.e. more than one) EpiDoc files.
    """

    _docs: Generator[EpiDoc, None, None] | list[EpiDoc]

    def __add__(self, other: EpiDocCorpus) -> EpiDocCorpus:

        if not isinstance(other, EpiDocCorpus):
            raise TypeError("Cannot append: item to "
                            "be appended is of type "
                            f"{type(other)}; " 
                            "required: EpiDocCorpus")

        return EpiDocCorpus(list(set(self.docs + other.docs)))

    @overload
    def __init__(
        self,
        inpt: EpiDocCorpus
        ):

        """
        :param inpt: EpiDocCorpus object
        """
        ...

    @overload
    def __init__(
        self,
        inpt: list[EpiDoc]
        ):

        """
        :param inpt: EpiDocCorpus object
        """
        ...

    @overload
    def __init__(
        self,
        inpt: str
    ):
        """
        :param inpt: path to the corpus as a str
        """
        ...

    @overload
    def __init__(
        self,
        inpt: Path
    ):
        """
        :param inpt: path to the corpus as a Path object
        """
        ...

    def __init__(
        self, 
        inpt: EpiDocCorpus | list[EpiDoc] | str | Path 
    ):

        def _handle_fp(_p: Path) -> None:

            if not _p.exists():
                raise FileExistsError(f'Directory {inpt} does not exist.')
            
            if not _p.is_dir():
                raise FileExistsError(f'Path {inpt} is not a directory.')

            self._docs = (EpiDoc(fp) for fp in _p.iterdir()
                          if fp.suffix == '.xml')

        # inpt is an EpiDocCorpus
        if isinstance(inpt, EpiDocCorpus):
            self._docs = inpt.docs
            return
        
        # inpt is a list of EpiDoc
        if isinstance(inpt, list):
            if inpt == []:
                self._docs = []
                return

            if isinstance(inpt[0], EpiDoc):
                inpt = cast(list[EpiDoc], inpt)
                self._docs = [doc for doc in inpt]

            return

        # inpt is a path
        elif isinstance(inpt, str):
            _handle_fp(Path(inpt))
            return

        elif isinstance(inpt, Path):
            _handle_fp(inpt)
            return
        
        raise TypeError("Invalid input type.")
    
    def __repr__(self) -> str:
        return f'EpiDocCorpus( doc_count = {self.doc_count} )'

    @property
    def datemin(self) -> int:
        not_afters = [doc.not_after 
                      for doc in self.docs if doc.not_after is not None]
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
    def _doc_to_xml_file(dstfolder: str | Path, doc: EpiDoc) -> None:
        
        "Writes out an EpiDoc object to an XML file"
        dstfolder_path = Path(dstfolder)
        if not dstfolder_path.exists():
            raise FileExistsError(f'Folder {dstfolder} does not exist')

        dst = dstfolder_path / Path(doc.id + '.xml')
        
        doc.to_xml_file(dst.absolute())

    @cached_property
    def docs(self) -> list[EpiDoc]:
        try:
            return list(sorted(self._docs, key=lambda doc: doc.id))
        except XMLSyntaxError as e:
            print('XMLSyntaxError in docs')
            print(e)
            return []
        except Exception as e:
            print('Exception in docs')
            print(e)
            return []

    @cached_property
    def docs_dict(self) -> dict[str, EpiDoc]:
        return {doc.id: doc for doc in self.docs}
    
    @cached_property
    def empty_corpus(self) -> EpiDocCorpus:
        return EpiDocCorpus([])

    @property
    def expans(self) -> list[Expan]:
        return list(chain(*[doc.expans for doc in self.docs]))

    def filter_by_dateafter(self, start: int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs
            if (doc.not_before is not None and doc.not_before >= start) 
            or (doc.date is not None and doc.date >= start)]

        return EpiDocCorpus(docs)

    def filter_by_daterange(self, start: int, end: int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs
            if doc.not_before is not None and doc.not_after is not None
            and doc.not_before >= start and doc.not_after <= end]
        
        return EpiDocCorpus(docs)

    def filter_by_form(
        self, 
        forms: list[str], 
        set_relation=SetRelation.intersection,
        ignore_case: bool=True
    ) -> EpiDocCorpus:
        
        if ignore_case:
            forms_lower = [form.lower() for form in forms]
            docs = [doc for doc in self.docs
                if set_relation(set(forms_lower), [form.lower() for form in doc.forms])]  
        else:
            docs = [doc for doc in self.docs
                if set_relation(set(forms), doc.forms)]  

        return EpiDocCorpus(inpt=docs)

    def filter_by_has_gap(
        self,
        has_gap=False,
        reasons:list[str]=[]
    ) -> EpiDocCorpus:
    
        docs = [doc for doc in self.docs
            if doc.has_gap(reasons=reasons) == has_gap]
        
        return EpiDocCorpus(docs)

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
        
        return EpiDocCorpus(docs)
    
    def filter_by_idrange(self, start: int, end: int) -> EpiDocCorpus:
        _int_range = range(start, end + 1)
        _str_range = [self.prefix + str(item).zfill(6) 
                      for item in _int_range]
        
        return self.filter_by_ids(ids=_str_range)

    def filter_by_ids(self, ids: list[str]) -> EpiDocCorpus:
        """
        Returns a new EpiDocCorpus containing the documents with 
        the ids in the ids list of strings
        """
        ids_ = [id for id in ids if id in self.docs_dict.keys()]
        return EpiDocCorpus([self.docs_dict[id] for id in ids_])

    def filter_by_languages(self, 
        langs: list[str], 
        set_relation: Callable[[set, set], bool]=SetRelation.intersection,
        language_attr: Literal['langs'] | Literal['div_langs']='langs'
    ) -> EpiDocCorpus:
        
        """
        Returns a copy of the corpus filtered by the 
        languages provided in the 'langs' parameter.
        Uses the 'textLang' element in the EpiDoc.
        """

        docs = [doc for doc in self.docs
            if set_relation(set(langs), doc.get_lang_attr(language_attr))]
        
        return EpiDocCorpus(docs)

    def filter_by_lemmata(
        self, 
        lemmata:list[str], 
        set_relation=SetRelation.intersection
    ) -> EpiDocCorpus:
    
        docs = [doc for doc in self.docs
            if set_relation(set(lemmata), doc.lemmata)]  

        return EpiDocCorpus(docs)

    def filter_by_materialclass(
        self, 
        materialclasses: list[str], 
        string_relation: Literal['equal', 'substring']
    ) -> EpiDocCorpus:

        """
        Return a subcorpus where the material classes of each 
        doc are either exactly equal to or contain at least 
        one of the strings in *materialclasses*,
        according to the value of the parameter *string_relation*
        """
#
        def filterstr(s1: str, s2: str) -> bool:
            if string_relation == 'equal':
                return s1 == s2
            
            if string_relation == 'substring':
                return s1 in s2
        
        docs = list[EpiDoc]()

        for doc in self.docs:
            for doc_material in doc.materialclasses:
                for q_material in materialclasses:
                    if filterstr(q_material, doc_material):
                        docs.append(doc)

        return EpiDocCorpus(docs)

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

        return EpiDocCorpus(docs)

    def filter_by_textclass(
        self, 
        textclasses: list[str | TextClass], 
        set_relation: Callable[[set[str], set[str]], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:

        # Convert input textclasses to their string representation
        _textclasses = list(map(str, textclasses))
    
        docs = [doc for doc in self.docs
            if set_relation(set(_textclasses), set(doc.textclasses))]

        return EpiDocCorpus(docs)

    @property
    def formatted_text(self) -> str:
        return ''.join([doc.formatted_text for doc in self.docs])          

    def get_doc_by_id(self, id:str) -> Optional[EpiDoc]:
        docs = self.filter_by_ids([id]).docs
        if docs == []:
            return None
        
        if len(docs) > 1:
            raise ValueError(f"More than one doc with id {id}.")
        
        return docs[0]

    @property
    def id_carriers(self) -> list[EpiDocElement]:
        return list(chain(*[doc.id_carriers for doc in self.docs]))

    @cached_property
    def ids(self) -> list[str]:
        return [doc.id for doc in self.docs
                if doc.id is not None]

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

    @property
    def materialclasses(self) -> set[str]:
        """
        Set of material classes in the corpus
        """

        return set(chain(*[doc.materialclasses for doc in self.docs]))

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
                doc=doc)

    @cached_property
    def size(self) -> int:
        return len(self.docs)

    def test_token_ids_unique(self, verbose: bool=False) -> bool:
        """
        Returns True if all token ids in the corpus
        are unique
        """

        ids = list(map(lambda token: token.id_xml or '', self.id_carriers))
        id_set = list(set(ids))

        if verbose:
            print('Total id carrying tokens: ', len(ids))
            print('Total unique ids: ', len(id_set))

        return len(ids) == len(id_set)

    @cached_property
    def textclasses(self) -> set[str]:
        return set([textclass for doc in self.docs 
                    for textclass in doc.textclasses])

    def to_txt(self, dst: str) -> None:
        """
        Writes a .txt file with the text of the documents
        in the corpus.
        """
        with open(dst, 'w') as f:
            f.write(self.formatted_text)

    def tokenize_to_folder(
        self, 
        dstfolder: str | Path, 
        add_space_between_words: bool=True,
        prettify_edition: bool=True,
        set_ids: bool=False,
        convert_ws_to_names: bool=True,
        verbose: bool=True
    ) -> None:

        """
        Tokenizes the corpus and writes out the files 
        to dstfolder.
        """

        for doc in sorted(self.docs, key=lambda doc: doc.id):
            if verbose: 
                print('Tokenizing', doc.id)

            doc.tokenize(
                prettify_edition=prettify_edition, 
                add_space_between_words=add_space_between_words, 
                set_ids=set_ids, 
                convert_ws_to_names=convert_ws_to_names, 
                verbose=verbose
            )
            
            self._doc_to_xml_file(
                dstfolder, 
                doc
            )

    @property
    def token_count(self) -> int:
        return sum([doc.token_count for doc in self.docs])

    @property
    def tokens(self) -> list[Token]:
        return list(chain(*[doc.tokens_no_nested for doc in self.docs]))
    
    def top(self, length=10) -> EpiDocCorpus:
        return EpiDocCorpus(list(top(self.docs, length)))