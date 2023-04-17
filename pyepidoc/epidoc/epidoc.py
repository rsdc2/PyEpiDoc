from __future__ import annotations
from typing import Optional, Union
from lxml import etree # type: ignore
from lxml.etree import _Element  # type: ignore

from ..base.element import Element
from ..base.root import Root
from ..utils import flatlist, maxone
from ..file import FileInfo, FileMode

from .edition import Edition
from .expan import Expan
from .abbr import AbbrInfo
from .epidoctypes import (
    TokenInfo, 
    Morphology, 
    SpaceUnit
)

from .token import Token
from ..constants import SET_IDS, SPACE_WORDS


class EpiDoc(Root):

    """
    This class provides services for interacting with individual
    EpiDoc files.
    It is therefore the domain of metadata such as 
    date, authority etc.
    as well as that for accessing the editions present
    in the file.
    """

    def __bytes__(self) -> bytes:
        return etree.tostring(
            self.e, 
            pretty_print=True, 
            encoding='utf-8', 
            xml_declaration=True
        )

    def __repr__(self) -> str:
        return f'EpiDoc(id="{self.id}")'

    def __str__(self) -> str:
        return str(bytes(self))


    @property
    def abbr_infos(self) -> set[AbbrInfo]:
        _abbr_infos = [token.abbr_info for token in self.tokens]
        return set(_abbr_infos)

    @property
    def apparatus(self) -> list[_Element]:
        return self.get_div_descendants('apparatus')

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
    def compound_words(self) -> list[Element]:
        return [item for edition in self.editions 
            for item in edition.compound_tokens]

    def convert_ws_to_names(self) -> EpiDoc:
        """Converts all <w> to <name> in place if they begin with a capital."""
        for edition in self.editions:
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
    def div_langs(self) -> set[str]:
        """Used by I.Sicily to host language information."""
        textpart_langs = [textpart.lang 
            for edition in self.editions 
                for textpart in edition.textparts
                    if textpart.lang is not None]

        edition_langs = [edition.lang for edition in self.editions 
            if edition.lang is not None]

        combined = textpart_langs + edition_langs

        return set(combined)

    @property
    def edition_text(self) -> str:
        return ''.join([edition.text_desc for edition in self.editions])

    @property
    def editions(self) -> list[Edition]:
        editions = self.get_div_descendants('edition')
        return [Edition(edition) for edition in editions]

    @property
    def first_edition(self) -> Optional[Edition]:
        return self.editions[0] if self.editions != [] else None

    def prettify_edition(
        self, 
        spaceunit=SpaceUnit.Space, 
        number=4, 
        verbose=True
    ) -> None:
    
        if verbose: 
            print(f'Prettifying {self.id}...')

        for edition in self.editions:
            edition.prettify(spaceunit=spaceunit, number=number)

    @property
    def expans(self) -> list[Expan]:
        return flatlist([edition.expans for edition in self.editions])

    @property
    def formatted_text(self) -> str:
        _text = '\n'.join([edition.formatted_text for edition in self.editions])
        return f'\n{self.id}\n{len(self.id) * "-"}\n{_text}\n'

    @property
    def forms(self) -> set[str]:
        return set([str(word) for word in self.tokens])

    @property
    def id(self) -> str:

        def get_idno_elems(s:str) -> list[Element]:
            if self.publication_stmt is None:
                return []

            return self.publication_stmt.get_desc_elems_by_name('idno', {'type': s})            

        idno_elem = None

        if self.authority == 'Epigraphische Datenbank Heidelberg':
            idno_elems = get_idno_elems('localID')
            idno_elem = maxone(idno_elems)

        elif self.authority == 'I.Sicily':
            idno_elems = get_idno_elems('filename')
            idno_elem = maxone(idno_elems)

        if idno_elem is None:
            return '[None]'

        return idno_elem.text

    @property
    def ismultilingual(self) -> bool:
        return len(self.div_langs) > 1 

    @property
    def gaps(self) -> list[Element]:
        items = [edition.gaps for edition in self.editions]
        return [item for item in flatlist(items)]

    def _get_daterange_attrib(self, attrib_name:str) -> Optional[int]:
        if self.orig_date is None:
            return None

        daterange_val = self.orig_date.get_attrib(attrib_name)

        try:
            return int(daterange_val) if daterange_val is not None else None
        except ValueError:
            return None

    @property
    def lang_usages(self) -> Optional[set[str]]:

        """Used by EDH to host language information."""

        language_elems = [Element(language) for language in self.get_desc('langUsage')]
        lang_usage = maxone(language_elems, None)

        if lang_usage is None: 
            return None

        languages = lang_usage.get_desc_elems_by_name('language')
        idents = [language.get_attrib('ident') for language in languages]
        return set([ident for ident in idents if ident is not None])

    @property
    def lemmata(self) -> set[str]:
        _lemmata = [word.lemma for word in self.tokens 
            if word.lemma is not None]

        return set(_lemmata)

    @property
    def morphologies(self) -> set[Morphology]:
        _morphologies = [word.morphology for word in self.tokens]
        return set(_morphologies)

    @property
    def not_after(self) -> Optional[int]:
        return self._get_daterange_attrib('notAfter-custom')

    @property
    def not_before(self) -> Optional[int]:
        return self._get_daterange_attrib('notBefore-custom')

    @property
    def orig_date(self) -> Optional[Element]:
        # TODO consider all orig_dates: at the moment only does the first        
        orig_date = maxone(
            self.get_desc('origDate'),
            defaultval=None,
            throw_if_more_than_one=False
        )
        if orig_date is None:
            return None

        if orig_date.attrib == dict():
            orig_date = maxone(Element(orig_date).get_desc('origDate'), throw_if_more_than_one=False)    

        if orig_date is None:
            return None        

        return Element(orig_date)

    @property
    def publication_stmt(self) -> Optional[Element]:
        publication_stmt = maxone(self.get_desc('publicationStmt'))
        if publication_stmt is None:
            return None
        return Element(publication_stmt)

    @property
    def prefix(self) -> str:
        if self.authority == "I.Sicily":
            return "ISic"
        elif self.authority == "Epigraphische Datenbank Heidelberg":
            return "HD"
        
        return ""

    def set_ids(self, override:bool=False) -> None:
        if SET_IDS or override:
            for edition in self.editions:
                edition.set_ids(override)

    def set_uuids(self) -> None:
        if SET_IDS:
            for edition in self.editions:
                edition.set_uuids()

    def add_space_between_tokens(self, override:bool=True) -> None:
        if SPACE_WORDS or override:
            for edition in self.editions:
                edition.space_words(override)

    @property
    def tei(self) -> Optional[Element]:
        return maxone(self.get_desc('TEI'))

    @property
    def tei_header(self) -> Optional[Element]:
        return maxone(self.get_desc('teiHeader'))

    @property
    def textclasses(self) -> list[str]:
        textclass_element = maxone(self.get_desc('textClass'))

        if textclass_element is None:
            return []

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
    def textlangs(self) -> Optional[set[str]]:
        """
        Used by I.Sicily to host language information.
        Returns lang_usages if there are no textlangs.
        """
        textlang = maxone([Element(textlang) 
            for textlang in self.get_desc('textLang')])
        
        if textlang is None: 
            return set()
        
        mainlang = textlang.get_attrib('mainLang')
        otherLang = textlang.get_attrib('otherLangs')
        
        if mainlang is None:
            return set()

        if otherLang is None:
            langs = [mainlang]
        else:
            langs = [mainlang] + otherLang.split()

        if len(langs) == 0:
            return self.lang_usages

        return set(langs)

    def to_xml(
        self, 
        dst:str, 
        verbose=True, 
        create_folderpath=False,
        fullpath=False
    ) -> None:

        dst_fileinfo = FileInfo(
            filepath=dst,
            mode=FileMode.w,
            create_folderpath=create_folderpath,
            fullpath=fullpath
        )

        if verbose: 
            print(f'Writing {self.id}...')
        
        with open(dst_fileinfo.full_filepath, 'wb') as f:
            f.write(bytes(self))

    def tokenize(self, verbose=True) -> None:
        if verbose: 
            print(f'Tokenizing {self.id}...')

        for edition in self.editions:
            edition.tokenize()

    @property
    def translation(self) -> _Element:
        return self.get_div_descendants('apparatus')

    @property
    def token_infos(self) -> set[TokenInfo]:
        _word_infos = [word.word_info for word in self.tokens]
        return set(_word_infos)

    @property
    def tokencount(self) -> int:
        return len(self.tokens)

    @property
    def tokens(self) -> list[Token]:
        tokens = [token for edition in self.editions 
            for token in edition.tokens]
        return tokens

    @property
    def tokens_list_str(self) -> list[str]:
        return [str(word) for edition in self.editions 
            for word in edition.tokens]

    @property
    def tokens_str(self) -> str:
        return ' '.join(self.tokens_list_str)
