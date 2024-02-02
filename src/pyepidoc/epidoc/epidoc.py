from __future__ import annotations
from typing import Optional, Literal, overload
from lxml.etree import (
    _Element, 
    _ElementTree
)
from pathlib import Path
from itertools import chain
import inspect

import pyepidoc
from pyepidoc.xml.docroot import DocRoot
from pyepidoc.utils import (
    maxone, 
    listfilter, 
    head,
    remove_none
)
from pyepidoc.types import Base

from .token import Token
from .errors import TEINSError, EpiDocValidationError
from .element import EpiDocElement, BaseElement
from .elements.edition import Edition
from .elements.expan import Expan
from .enums import (
    SpaceUnit,
    AbbrType
)



class EpiDoc(DocRoot):

    """
    This class provides services for interacting with individual
    EpiDoc files.
    It is therefore the domain of metadata such as 
    date, authority etc.
    as well as that for accessing the editions present
    in the file.
    """

    def __repr__(self) -> str:
        return f'EpiDoc(id="{self.id}")'

    def __str__(self) -> str:
        return str(bytes(self))

    def __eq__(self, other) -> bool:
        if not isinstance(other, EpiDoc):
            raise TypeError(f'Cannot compare type EpiDoc with {type(other)}')
        
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __init__(
            self, 
            inpt: Path | str | _ElementTree,
            validate_on_load: bool=False):
        
        """
        Initialize an EpiDoc object on a given input 
        (string, Path or lxml _ElementTree).
        On load checks that the file has the TEI namespace 
        "http://www.tei-c.org/ns/1.0" declared.

        :param inpt: string (containing path to document), 
            Path or lxml _ElementTree

        :param validate_on_load: if True, validates against 
            EpiDoc RelaxNG schema, "tei-epidoc.rng", found in the root 
            directory of the package
        """
        
        super().__init__(inpt)
        self.assert_has_TEIns()

        if validate_on_load:
            module_path = inspect.getfile(pyepidoc)
            rng_path = Path(module_path).parent / Path('tei-epidoc.rng')
            validation_result, msg = self.validate_relaxng(rng_path)
            
            if not validation_result:
                raise EpiDocValidationError(msg)

    @property
    def apparatus(self) -> list[_Element]:
        return self.get_div_descendants('apparatus')
    
    def assert_has_TEIns(self) -> bool:
        """
        Return True if uses TEI namespaces;
        raises an AssertionError if not
        """

        if not 'http://www.tei-c.org/ns/1.0' in self.e.nsmap.values():
            raise TEINSError()
        
        return True

    @property
    def authority(self) -> Optional[str]:
        if self.publication_stmt is None:
            return None

        elem = maxone(self
            .publication_stmt
            .get_desc_elems_by_name('authority'), 
        )

        if elem is None:
            return None
        
        return elem.text

    @property
    def commentary(self) -> list[_Element]:
        return self.get_div_descendants('commentary')

    @property
    def compound_words(self) -> list[EpiDocElement]:
        return [item for edition in self.editions() 
            for item in edition.compound_tokens]

    def convert_ids(self, oldbase: Base, newbase: Base) -> None:
        """
        Put IDs (xml:id) on all elements of the edition,
        in place
        """
        for edition in self.editions():
            edition.convert_ids(oldbase, newbase)
    
    def convert_ws_to_names(self) -> EpiDoc:
        """
        Converts all <w> to <name> in place if they 
        begin with a capital.
        """
        
        for edition in self.editions():
            edition.convert_words_to_names()
        
        return self

    @property
    def date(self) -> Optional[int]:
        if self.orig_date is None:
            return None
            
        date = self.orig_date.get_attrib('when-custom')

        try:
            return int(date) if date is not None else None
        except ValueError:
            return None

    @property
    def date_range(self) -> tuple[Optional[int], Optional[int]]:
        _date_range = (self.not_before, self.not_after)

        if _date_range == (None, None):
            return (self.date, self.date)
        
        return _date_range
        
    @property
    def date_mean(self) -> Optional[int]:
        not_before, not_after = self.date_range
        if not_before is None or not_after is None:
            return None
    
        mean = (not_before + not_after) / 2
        return int(mean)

    @property
    def distributor(self) -> Optional[str]:
        """
        IRT (Tripolitania) does not use <authority>
        """

        if self.publication_stmt is None:
            return None

        elem = maxone(self
            .publication_stmt
            .get_desc_elems_by_name('distributor'), 
        )

        if elem is None:
            return None
        
        return elem.text

    @property
    def div_langs(self) -> set[str]:

        """Used by I.Sicily to host language information."""
        
        textpart_langs = [textpart.lang 
            for edition in self.editions()
                for textpart in edition.textparts
                    if textpart.lang is not None]

        edition_langs = [edition.lang for edition in self.editions()
            if edition.lang is not None]

        combined = textpart_langs + edition_langs

        return set(combined)

    @property
    def edition_text(self) -> str:
        return ''.join([edition.text_desc for edition in self.editions()])

    def editions(self, include_transliterations=False) -> list[Edition]:
        editions = [Edition(edition) 
            for edition in self.get_div_descendants('edition')]

        if include_transliterations:
            return editions

        else:
            return listfilter(lambda edition: edition.subtype != 'transliteration', editions)

    @property
    def expans(self) -> list[Expan]:
        """
        Returns a list of abbreviated items (including both abbreviation and expansion)
        """
        
        return list(chain(*[edition.expans 
                         for edition in self.editions()]))

    def expans_by_type(self, abbr_type:Optional[AbbrType]) -> list[Expan]:
        """
        Returns all the expans of the type specified in abbr_type.
        If abbr_type is None, returns all the expans.
        """
        if abbr_type is None:
            return self.expans
        
        return [expan for expan in self.expans 
                if expan.abbr_types == abbr_type]
                       
    @property
    def first_edition(self) -> Optional[Edition]:
        return self.editions()[0] if self.editions != [] else None

    @property
    def formatted_text(self) -> str:
        _text = '\n'.join([edition.formatted_text 
                           for edition in self.editions()])
        return f'\n{self.id}\n{len(self.id) * "-"}\n{_text}\n'

    @property
    def forms(self) -> set[str]:
        return set([str(word) for word in self.tokens])

    @property
    def gaps(self) -> list[EpiDocElement]:
        items = [edition.gaps for edition in self.editions()]
        return [item for item in list(chain(*items))]

    def get_lang_attr(
            self, 
            lang_attr: Literal['div_langs'] | Literal['langs']
        ) -> set[str]:
        
        if lang_attr == 'div_langs':
            return self.div_langs
        
        elif lang_attr == 'langs':
            return set(self.langs)
        
        raise ValueError(f'Invalid lang_attr {lang_attr}')

    def has_gap(self, reasons: list[str]=[]) -> bool:

        """
        Returns True if the document contains a <gap> element with a reason
        contained in the "reasons" attribute.
        If "reasons" is set to an empty list, 
        returns True if there are any gaps regardless of reason.
        """

        if self.gaps == []:
            return False
        
        # There must be gaps
        if reasons == []:
            return True

        for gap in self.gaps:
            doc_gap_reasons = gap.get_attrib('reason')
            if doc_gap_reasons is None:
                continue
            doc_gap_reasons_split = doc_gap_reasons.split()
            intersection = set(reasons).intersection(set(doc_gap_reasons_split))

            if len(intersection) > 0:
                return True

        return False

    @property
    def has_supplied(self) -> bool:
        return self.supplied != []

    @property
    def id(self) -> str:

        """
        The document ID, e.g. ISic000001-00001
        """

        def get_idno_elems(s: str) -> list[BaseElement]:
            if self.publication_stmt is None:
                return []

            return self.publication_stmt.get_desc_elems_by_name('idno', {'type': s})            

        id_sources = {
            'Epigraphische Datenbank Heidelberg': 'localID',
            'I.Sicily': 'filename',
            'Università di Bologna': 'localID',
            'King’s College London': 'filename'
        }

        if self.authority is None:
            return 'None'
        
        source = id_sources.get(self.authority)

        if source is None:
            return 'None'
        
        idno_elems = get_idno_elems(s=source)
        idno_elem = maxone(idno_elems)

        if idno_elem is None:
            return 'None'

        return idno_elem.text

    @property
    def ids(self) -> list[str]:
        """
        The element IDs in the editions of the document
        """

        abs = chain(*[edition.abs 
                      for edition in self.editions()])
        elems = chain(*[ab.id_carriers for ab in abs])

        return [elem.id_xml for elem in elems 
                if elem.id_xml is not None]

    @property
    def id_carriers(self) -> list[EpiDocElement]:
        return list(chain(*[edition.id_carriers 
                            for edition in self.editions()]))

    @property
    def is_multilingual(self) -> bool:
        return len(self.div_langs) > 1 

    def _get_daterange_attrib(self, attrib_name:str) -> Optional[int]:
        if self.orig_date is None:
            return None

        daterange_val = self.orig_date.get_attrib(attrib_name)

        try:
            return int(daterange_val) if daterange_val is not None else None
        except ValueError:
            return None

    @property
    def lang_usages(self) -> list[str]:

        """Used by EDH to host language information."""

        language_elems = [EpiDocElement(language) 
                          for language in self.get_desc('langUsage')]
        lang_usage = maxone(language_elems, None)

        if lang_usage is None: 
            return []

        languages = lang_usage.get_desc_elems_by_name('language')
        idents = [language.get_attrib('ident') for language in languages]
        return [ident for ident in idents if ident is not None]

    @property
    def langs(self) -> list[str]:
        """
        Returns lang_usages if there are no textlangs.
        """
        
        if self.mainlang is None:
            return self.otherlangs

        langs = [self.mainlang] + self.otherlangs

        if len(langs) == 0:
            return self.lang_usages

        return langs

    @property
    def mainlang(self) -> Optional[str]:
        if self.textlang is None:
            return None
        return self.textlang.get_attrib('mainLang')

    @property
    def mean_date(self) -> int | None:
        return self.date_mean

    @property
    def otherlangs(self) -> list[str]:
        if self.textlang is None:
            return []
        
        otherlangs = self.textlang.get_attrib('otherLangs')
        
        if otherlangs is None:
            return []

        return otherlangs.split()

    @property
    def lemmata(self) -> set[str]:
        _lemmata = [word.lemma for word in self.tokens 
            if word.lemma is not None]

        return set(_lemmata)

    @property
    def materialclasses(self) -> list[str]:

        material_e = self.get_desc('material')
        
        if material_e is None:
            return []
        
        return remove_none([EpiDocElement(e).get_attrib('ana') 
                            for e in material_e])

    @property
    def not_after(self) -> Optional[int]:
        return self._get_daterange_attrib('notAfter-custom')

    @property
    def not_before(self) -> Optional[int]:
        return self._get_daterange_attrib('notBefore-custom')

    @property
    def orig_date(self) -> Optional[EpiDocElement]:
        # TODO consider all orig_dates: at the moment only does the first        
        orig_date = maxone(
            self.get_desc('origDate'),
            defaultval=None,
            throw_if_more_than_one=False
        )
        if orig_date is None:
            return None

        if orig_date.attrib == dict():
            orig_date = maxone(
                EpiDocElement(orig_date).get_desc('origDate'), 
                throw_if_more_than_one=False
            )    

        if orig_date is None:
            return None        

        return EpiDocElement(orig_date)

    @property
    def orig_place(self) -> str:
        xpath_results = self.xpath('//ns:history/ns:origin/'
                                   'ns:origPlace/ns:placeName'
                                   '[@type="ancient"]/text()')
        result = head(
            xpath_results, 
            throw_if_more_than_one=False
        )

        if result is None:
            return 'None'
        
        return str(result)

    @property
    def prefix(self) -> str:
        if self.authority == "I.Sicily":
            return "ISic"
        elif self.authority == "Epigraphische Datenbank Heidelberg":
            return "HD"
        
        return ""

    def prettify_edition(
        self, 
        spaceunit=SpaceUnit.Space, 
        number=4, 
        verbose=True
    ) -> None:

        """
        Prettify the xml of the <div type="edition"> element; this
        cannot be done automatically using lxml since this element
        will have @xml:space="preserve".
        """
    
        if verbose: 
            print(f'Prettifying {self.id}...')

        for edition in self.editions():
            edition.prettify(spaceunit=spaceunit, number=number)

    @property
    def publication_stmt(self) -> Optional[EpiDocElement]:
        publication_stmt = maxone(self.get_desc('publicationStmt'))
        if publication_stmt is None:
            return None
        return EpiDocElement(publication_stmt)

    def set_ids(self, base: Base=52) -> None:
        """
        Put IDs (xml:id) on all elements of the edition,
        in place
        """
        for edition in self.editions():
            edition.set_ids(base)

    def space_tokens(self) -> None:
        for edition in self.editions():
            edition.space_tokens()

    @property
    def supplied(self) -> list[BaseElement]:
        return list(chain(*[edition.supplied for edition in self.editions()]))

    @property
    def tei(self) -> Optional[_Element]:
        return maxone(self.get_desc('TEI'))

    @property
    def tei_header(self) -> Optional[_Element]:
        return maxone(self.get_desc('teiHeader'))

    @property
    def textclasses(self) -> list[str]:
        textclass_e = maxone(self.get_desc('textClass'))

        if textclass_e is None:
            return []

        textclass_element = EpiDocElement(textclass_e)

        terms = textclass_element.get_desc_elems_by_name('term')
        terms_with_ana = [term for term in terms 
                                if term.has_attrib('ana')]

        functions = []
        for term in terms_with_ana:
            ana_term = term.get_attrib('ana')

            if ana_term is not None:
                functions += ana_term.split()

        return functions

    @property
    def textlang(self) -> Optional[EpiDocElement]:
        """
        Used by I.Sicily to host language information.        
        """

        textlang = maxone([EpiDocElement(textlang) 
            for textlang in self.get_desc('textLang')])
        
        if textlang is None: 
            return None

        return textlang

    @overload   
    def to_xml_file(
        self, 
        dst: Path, 
        verbose=True
    ) -> None:
        ...

    @overload
    def to_xml_file(
        self,
        dst: str
    ) -> None:
        ...

    def to_xml_file(
        self, 
        dst: Path | str, 
        verbose=True
    ) -> None:
        
        """
        Writes out the XML to file
        """
        if isinstance(dst, Path):
            p = dst
        else:
            p = Path(dst)

        if not p.parent.exists():
            raise FileExistsError(f'Directory {p.parent.absolute()} does not exist.')

        if verbose: 
            print(f'Writing {self.id}...')
        
        with open(dst, 'wb') as f:
            f.write(bytes(self))

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    def tokenize(
        self, 
        add_space_between_words:bool=True,
        prettify_edition:bool=True,
        set_ids:bool=False,
        convert_ws_to_names:bool=False,
        verbose:bool=True
    ) -> EpiDoc:
        
        """
        Tokenizes the EpiDoc document in place.
        """

        if verbose: 
            print(f'Tokenizing {self.id}...')

        for edition in self.editions():
            edition.tokenize()

        if add_space_between_words:
            self.space_tokens()
        
        if convert_ws_to_names:
            self.convert_ws_to_names()

        if set_ids:
            self.set_ids(100)
            
        if prettify_edition:
            self.prettify_edition(spaceunit=SpaceUnit.Space, number=4)

        return self

    @property
    def tokens(self) -> list[Token]:
        tokens = [token for edition in self.editions()
                    for token in edition.tokens]
        return tokens

    @property
    def tokens_list_str(self) -> list[str]:
        return list(chain(*[edition.tokens_list_str 
                            for edition in self.editions()]))
    
    @property
    def tokens_normalized(self) -> list[Token]:

        """
        Returns list of tokens of the <div type="edition">.
        If the normalised form is an empty string,
        does not include the token.
        """

        return list(chain(*[edition.tokens_normalized 
                            for edition in self.editions()]))

    @property
    def tokens_str(self) -> str:
        return ' '.join(self.tokens_list_str)
    
    @property
    def translation(self) -> list[_Element]:
        return self.get_div_descendants('apparatus')

    @property
    def w_tokens(self) -> list[Token]:
        return list(chain(*[edition.w_tokens 
                            for edition in self.editions()]))
