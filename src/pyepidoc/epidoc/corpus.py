from __future__ import annotations
from typing import (
    Callable,
    Optional, 
    Sequence, 
    overload, 
    cast, 
    Literal, 
    Generator,
    SupportsIndex
)
from functools import cached_property
from itertools import chain
from pathlib import Path

from lxml.etree import XMLSyntaxError  

from pyepidoc.shared.classes import SetRelation
from pyepidoc.shared.utils import maxone, top, remove_none
from pyepidoc.shared.numbers import percentage
from pyepidoc.shared.string import format_year
from pyepidoc.epidoc.generic_collection import GenericCollection

from .abbreviations import Abbreviations
from .epidoc import EpiDoc
from .element import EpiDocElement
from .token import Token
from .elements.expan import Expan
from .elements.name import Name
from .elements.g import G
from .elements.num import Num
from .enums import TextClass
from .elements.role_name import RoleName
from .elements.pers_name import PersName


class EpiDocCorpus:

    """
    Provides an interface for handling a corpus of 
    (i.e. more than one) EpiDoc files.
    """

    _docs: Generator[EpiDoc, None, None] | list[EpiDoc]

    @overload
    def __init__(
        self,
        inpt: EpiDocCorpus,
        max_iter: int | None = None
        ):

        """
        :param inpt: EpiDocCorpus object

        :param max_iter: maximum number of items in the corpus. 
        Only applied where inpt is a path.
        """
        ...

    @overload
    def __init__(
        self,
        inpt: list[EpiDoc],
        max_iter: int | None = None
        ):

        """
        :param inpt: EpiDocCorpus object

        :param max_iter: maximum number of items in the corpus. 
        Only applied where inpt is a path.
        """
        ...

    @overload
    def __init__(
        self,
        inpt: str,
        max_iter: int | None = None
    ):
        """
        :param inpt: path to the corpus as a str

        :param max_iter: maximum number of items in the corpus. 
        Only applied where inpt is a path.
        """
        ...

    @overload
    def __init__(
        self,
        inpt: Path,
        max_iter: int | None = None
    ):
        """
        :param inpt: path to the corpus as a Path object

        :param max_iter: maximum number of items in the corpus. 
        Only applied where inpt is a path.
        """
        ...

    def __init__(
        self, 
        inpt: EpiDocCorpus | list[EpiDoc] | str | Path,
        max_iter: int | None = None
    ):

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

            raise TypeError('First member of list is not of type '
                            f'EpiDoc, but of type {type(inpt[0])}.')
        
        # inpt is a path
        elif isinstance(inpt, (str, Path)):
            self._handle_fp(inpt, max_iter=max_iter)
            return
        
        raise TypeError("Invalid input type.")
    
    def __add__(self, other: EpiDocCorpus) -> EpiDocCorpus:

        if not isinstance(other, EpiDocCorpus):
            raise TypeError("Cannot append: item to "
                            "be appended is of type "
                            f"{type(other)}; " 
                            "required: EpiDocCorpus")

        return EpiDocCorpus(list(set(self.docs + other.docs)))

    def __getitem__(self, i: SupportsIndex) -> EpiDoc:
        return self.docs[i]

    def __repr__(self) -> str:
        return f'EpiDocCorpus( doc_count = {self.doc_count} )'

    @property
    def abbreviations(self) -> Abbreviations:
        """
        Return an abbreviations object for doing queries on abbreviations
        """
        return Abbreviations(self.expans)
    
    @property
    def count(self) -> int:
        return self.doc_count

    @property
    def datemax(self) -> int:
        not_afters = remove_none([doc.not_after for doc in self.docs])
        dates = [doc.date for doc in self.docs 
            if doc.date is not None]

        return max(not_afters + dates)

    @property
    def datemin(self) -> int:
        not_befores = remove_none([doc.not_before for doc in self.docs])
        dates = [doc.date for doc in self.docs if doc.date is not None]

        return min(not_befores + dates)

    @property
    def daterange(self) -> tuple[int, int]:
        """
        Return the date range of the corpus as a whole
        as (min, max)
        """

        return (self.datemin, self.datemax)

    @property
    def dateranges(self) -> list[tuple[Optional[int], Optional[int]]]:
        return [doc.daterange for doc in self.docs]

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
    def _doc_to_xml_file(
        dstfolder: str | Path, 
        doc: EpiDoc,
        verbose: bool) -> None:
        
        """
        Writes out an EpiDoc object to an XML file
        """

        dstfolder_path = Path(dstfolder)
        if not dstfolder_path.exists():
            raise FileExistsError(f'Folder {dstfolder} does not exist')

        dst = dstfolder_path / Path(doc.id + '.xml')
        
        doc.to_xml_file(dst.absolute(), verbose=verbose)

    @cached_property
    def docs(self) -> list[EpiDoc]:
        _docs: list[EpiDoc] = []
        try:
            for doc in self._docs:
                _docs += [doc]
                _ = doc.id # Check ID valid
            
            return list(sorted(_docs, key=lambda doc: doc.id))
        
        except XMLSyntaxError as e:
            print('XMLSyntaxError in docs')
            print(e)
            return []
        except Exception as e:
            print(f'Error processing {_docs[-1].filename}. This may be to do with retrieving the ID. Original error message: ')
            print(e)
            return []
        
    @property
    def docs_with_no_or_empty_main_edition(self) -> list[EpiDoc]:
        """
        Return a list of EpiDoc objects where the 
        main edition is empty or None
        """
        return [doc for doc in self.docs
                if doc.main_edition is None or 
                    doc.has_no_main_edition]

    @cached_property
    def docs_dict(self) -> dict[str, EpiDoc]:
        return {doc.id: doc for doc in self.docs}
     
    @property
    def _edition_subtypes(self) -> set[str]:
        """
        Set of all subtypes on the editions 
        in the corpus
        """
        return set(chain(*[doc._edition_subtypes 
                           for doc in self.docs]))



    def empty_corpus(self) -> EpiDocCorpus:
        """
        Return a new empty EpiDocCorpus object
        """
        return EpiDocCorpus([])

    @property
    def expans(self) -> list[Expan]:
        """
        Return a list of Expan objects, that 
        contain information about abbreviations
        """
        return list(chain(*[doc.expans for doc in self.docs]))

    def filter_by_dateafter(self, start: int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs if doc.is_after(start)]

        return EpiDocCorpus(docs)
    
    def filter_by_datebefore(self, end: int) -> EpiDocCorpus:
        docs = [doc for doc in self.docs if doc.is_before(end)]

        return EpiDocCorpus(docs)

    def filter_by_daterange(self, start: int, end: int) -> EpiDocCorpus:
        
        docs = [doc for doc in self.docs
            if doc.is_after(start) and doc.is_before(end)]
        
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

    def filter_by_g_ref(
        self,
        g_refs: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        def _filter_by_rolename(doc: EpiDoc) -> bool:
            doc_g_refs = map(
                lambda g: g.ref, 
                doc.gs
            )
            if set_relation(set(g_refs), set(doc_g_refs)):
                return True
            
            return False

        docs = filter(_filter_by_rolename, self.docs)
        return EpiDocCorpus(list(docs))

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
        language_attr: Literal['langs'] | Literal['div_langs']='div_langs'
    ) -> EpiDocCorpus:
        
        """
        Returns a copy of the corpus filtered by the 
        languages 

        :param langauge_attr: If this is set to 'langs',
        uses the 'textLang' element in the EpiDoc. If this is 
        set to 'div_langs', looks at the @xml:lang attribute
        on the <div> elements in the edition.
        """

        docs = [doc for doc in self.docs
            if set_relation(set(langs), doc.get_lang_attr(language_attr))]
        
        return EpiDocCorpus(docs)

    def filter_by_lemmata(
        self, 
        lemmata: list[str], 
        set_relation = SetRelation.intersection
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

    def filter_by_name(
        self,
        names: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        """
        Filters the corpus according to the value
        of <name>.

        :param set_relation: a value of SetRelation
        """

        def filter_by_name(doc: EpiDoc) -> bool:
            doc_names = map(lambda name: name.form, doc.names())
            return set_relation(set(names), set(doc_names))

        docs = filter(filter_by_name, self.docs)  

        return EpiDocCorpus(list(docs))

    def filter_by_name_type(
        self,
        name_types: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        """
        Filters the corpus according to the value
        of <name>.

        :param set_relation: a value of SetRelation
        """

        def filter_by_name(doc: EpiDoc) -> bool:
            doc_name_types = map(lambda name: name.name_type, doc.names())
            return set_relation(set(name_types), set(doc_name_types))

        docs = filter(filter_by_name, self.docs)  

        return EpiDocCorpus(list(docs))

    def filter_by_num_value(
        self,
        min: int,
        max: int,
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        """
        Filters the corpus according to the value
        of <num>.

        :param set_relation: a value of SetRelation
        """

        num_values = map(str, range(min, max + 1))

        def _filter_by_num_value(doc: EpiDoc) -> bool:
            doc_num_values = map(lambda num: num.value, doc.nums)
            return set_relation(set(num_values), set(doc_num_values))

        docs = filter(_filter_by_num_value, self.docs)  

        return EpiDocCorpus(list(docs))

    def filter_by_orig_place(
        self,
        orig_places: list[str],
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

    def filter_by_pers_name_type(
        self,
        pers_name_types: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        def _filter_by_pers_name(doc: EpiDoc) -> bool:
            doc_pers_name_types = map(
                lambda pers_name: pers_name.pers_name_type, 
                doc.pers_names
            )
            if set_relation(set(pers_name_types), set(doc_pers_name_types)):
                return True
            
            return False

        docs = filter(_filter_by_pers_name, self.docs)
        return EpiDocCorpus(list(docs))

    def filter_by_role_name_subtype(
        self,
        role_name_subtypes: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        def _filter_by_rolename(doc: EpiDoc) -> bool:
            doc_role_subtypes = map(
                lambda rolename: rolename.role_name_subtype, 
                doc.role_names
            )
            if set_relation(set(role_name_subtypes), set(doc_role_subtypes)):
                return True
            
            return False

        docs = filter(_filter_by_rolename, self.docs)
        return EpiDocCorpus(list(docs))

    def filter_by_role_name_type(
        self,
        role_types: list[str],
        set_relation: Callable[[set, set], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:
        
        def _filter_by_rolename(doc: EpiDoc) -> bool:
            doc_role_name_types = map(
                lambda rolename: rolename.role_name_type, 
                doc.role_names
            )
            if set_relation(set(role_types), set(doc_role_name_types)):
                return True
            
            return False

        docs = filter(_filter_by_rolename, self.docs)
        return EpiDocCorpus(list(docs))

    def filter_by_textclass(
        self, 
        textclasses: list[str | TextClass], 
        set_relation: Callable[[set[str], set[str]], bool]=SetRelation.intersection
    ) -> EpiDocCorpus:

        # Convert input textclasses to their string representation
        _textclasses = list(map(str, textclasses))
    
        docs = [
            doc for doc in self.docs
            if set_relation(
                set(_textclasses), 
                set(doc.textclasses))
        ]

        return EpiDocCorpus(docs)
    
    @staticmethod
    def from_path(
        path: Path | str, 
        max_iter: int | None) -> EpiDocCorpus:

        """
        Return an EpiDoc corpus from a folder path

        :max_iter: Max number of items in the corpus
        """

        return EpiDocCorpus(path, max_iter)

    @property
    def formatted_text(self) -> str:
        return ''.join([doc.formatted_text for doc in self.docs])          

    @property
    def gs(self) -> list[G]:
        return list(chain(*[doc.gs for doc in self.docs]))

    def get_doc_by_id(self, id:str) -> Optional[EpiDoc]:
        docs = self.filter_by_ids([id]).docs
        if docs == []:
            return None
        
        if len(docs) > 1:
            raise ValueError(f"More than one doc with id {id}.")
        
        return docs[0]

    def _handle_fp(self, _p: Path | str, max_iter: int | None = None) -> None:

        if not Path(_p).exists():
            raise FileExistsError(f'Directory {_p} does not exist.')
        
        if not Path(_p).is_dir():
            raise FileExistsError(f'Path {_p} is not a directory.')

        iterations = 0

        if max_iter is None:
            self._docs = (EpiDoc(fp) for fp in Path(_p).iterdir()
                        if fp.suffix == '.xml')
            return
        else:
            docs: list[EpiDoc] = []
            for fp in Path(_p).iterdir():
                if fp.suffix == '.xml':
                    docs += [EpiDoc(fp)]
                    iterations += 1
                
                if iterations > max_iter:
                    break
            
            if iterations == 0:
                print('WARNING: No .xml files found in '
                      f'{_p}')
            self._docs = docs

    @property
    def id_carriers(self) -> list[EpiDocElement]:
        return list(chain(*[doc.id_carriers for doc in self.docs]))

    @cached_property
    def ids(self) -> list[str]:
        return [doc.id for doc in self.docs
                if doc.id is not None]
    
    def info(self, 
             name_predicate: Callable[[Name], bool]) -> str:

        """
        Provide key statistical information about the corpus
        """

        abbreviations = self.abbreviations.count
        suspensions = self.abbreviations.suspensions.count
        name_suspensions = (self.abbreviations.suspensions
                            .where_ancestor_is('name')
                            .map(lambda expan: expan.get_ancestors_by_name('name')[0]._e)
                            .map(lambda elem: Name(elem))
                            .where(name_predicate)
                            .count)
        name_abbrs = (self.abbreviations
                      .where_ancestor_is('name')
                      .map(lambda expan: expan.get_ancestors_by_name('name')[0]._e)
                      .map(lambda elem: Name(elem))
                      .where(name_predicate)
                      .count)
        names_count = len(self.names(name_predicate))
        indent = '\t\t\t\t'

        return  (
            f'Document count:{indent}{self.doc_count}\n'
            f'Date range:{indent}{format_year(self.daterange[0])}--{format_year(self.daterange[1])}\n'
            f'Token count:{indent}{self.token_count}\n'
            f'  - of which names (% tokens):\t\t{names_count} ({percentage(names_count, self.token_count)}%)\n'
            f'Abbreviations:{indent}{abbreviations}\n'
            f'  - of which suspensions (% abbrs.):\t{suspensions} ({percentage(suspensions, abbreviations)}%)\n'
            f'    -- of which names (% susp.):\t{name_suspensions} ({percentage(name_suspensions, suspensions)}%)\n'
            f'    -- of which names (% names):\t{name_suspensions} ({percentage(name_suspensions, names_count)}%)\n'
            f'  - name abbreviations (% names):\t{name_abbrs} ({percentage(name_abbrs, names_count)}%)'
        )

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
    
    @property
    def mean_token_count(self) -> float:
        """
        Return the mean number of tokens in each document
        """

        total = sum([doc.token_count for doc in self.docs])
        return total / self.doc_count

    def multilinguals(self, head: Optional[int]=None) -> list[EpiDoc]:
        """
        Return a list of EpiDoc objects where there is more than 
        one language mentioned in either the @xml:lang attribute 
        of the edition, or in the <textLang> element.

        :param head: take the top x number of EpiDoc, where x is defined in 
        @head. If `head` is None, returns all multilinguals.
        """

        docs = [doc for doc in self.docs if doc.is_multilingual]
        if head is not None and len(docs) > head:
            return docs[0:head]
        
        return docs

    def names(self, 
              predicate: Callable[[Name], bool] = lambda _: True
              ) -> GenericCollection[Name]:
        """
        Return a list of `Name` objects for all the
        <name> elements in the document's main edition.

        :param name_predicate: a function containing
        a condition for whether or not to include a name.
        Defaults to returning True.
        """
        names = list(chain(*[doc.names(predicate) for doc in self.docs]))
        return GenericCollection(names)

    @property
    def nums(self) -> list[Num]:
        return list(chain(*[doc.nums for doc in self.docs]))

    @property
    def pers_names(self) -> list[PersName]:
        return list(chain(*[doc.pers_names for doc in self.docs]))

    @cached_property
    def prefix(self) -> str:
        doc = maxone(self.docs, None, throw_if_more_than_one=True)
        if doc is None:
            return ''
        
        return doc.prefix

    def print_info(self, 
                   name_predicate: Callable[[Name], bool] = lambda _: True):
        
        """
        Print key statistical information about the corpus
        to stdout.
        """

        print(self.info(name_predicate=name_predicate))
    
    @property
    def role_names(self) -> list[RoleName]:
        return list(chain(*[doc.role_names for doc in self.docs]))

    def set_ids(
            self, 
            dstfolder: str,
            verbose=True
        ) -> None:
        
        for doc in self.docs:
            if verbose: print(f'Setting ids for {doc.id}...')
            doc.set_ids()
            self._doc_to_xml_file(
                dstfolder=dstfolder, 
                doc=doc,
                verbose=verbose)

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
        return self._get_textclasses(True)
    
    def _get_textclasses(self, throw_if_more_than_one: bool, ) -> set[str]:
        return set([textclass for doc in self.docs 
                    for textclass in doc._get_textclasses(
                        throw_if_more_than_one=throw_if_more_than_one)])

    def to_txt(self, dst: str) -> None:
        """
        Writes a .txt file with the text of the documents
        in the corpus.
        """
        with open(dst, 'w') as f:
            f.write(self.formatted_text)

    @property
    def token_count(self) -> int:
        return sum([doc.token_count for doc in self.docs])

    def tokenize_to_folder(
        self, 
        dstfolder: str | Path, 
        add_space_between_w_elements: bool=True,
        prettify_edition: bool=True,
        set_ids: bool=False,
        convert_ws_to_names: bool=True,
        verbose: bool=False
    ) -> None:

        """
        Tokenizes the corpus and writes out the files 
        to dstfolder.
        If a file cannot be tokenized, a message is printed
        to stdout and the file is not included in the 
        tokenized corpus.
        """

        for doc in sorted(self.docs, key=lambda doc: doc.id):
            if verbose: 
                print('Tokenizing', doc.id)

            try:
                if not doc.has_no_main_edition:
                    doc.tokenize(
                        prettify_edition=prettify_edition, 
                        add_space_between_words=add_space_between_w_elements, 
                        set_ids=set_ids, 
                        convert_ws_to_names=convert_ws_to_names, 
                        verbose=verbose
                    )
                else: 
                    print(f'Could not tokenize {doc.id}: no main edition found.')
            except ValueError as e:
                print(e)
                continue
            
            self._doc_to_xml_file(
                dstfolder, 
                doc,
                verbose
            )

    @property
    def tokens(self) -> list[Token]:
        return list(chain(*[doc.tokens_no_nested for doc in self.docs]))
    
    def top(self, length=10) -> EpiDocCorpus:
        return EpiDocCorpus(list(top(self.docs, length)))

    def where(self, predicate: Callable[[EpiDoc], bool]) -> EpiDocCorpus:
        """
        Filter abbreviations according to a predicate
        """

        return EpiDocCorpus(list(filter(predicate, self._docs)))