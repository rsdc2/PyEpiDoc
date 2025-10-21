from __future__ import annotations
from typing import (
    Optional, 
    Literal, 
    overload,
    Callable
)
from functools import cached_property

from lxml import etree
from lxml.etree import (
    _Element, 
    _ElementTree
)

from pathlib import Path
from itertools import chain
import inspect
import io
from io import BytesIO

from pyepidoc.tei.teidoc import TeiDoc


import pyepidoc
from pyepidoc.xml.docroot import DocRoot
from pyepidoc.shared import (
    maxone, 
    listfilter, 
    head,
    remove_none
)
from pyepidoc.shared.types import Base

from .token import Token
from .errors import TEINSError, EpiDocValidationError
from .epidoc_element import EpiDocElement, XmlElement

from .edition_elements.ab import Ab
from .body import Body
from .edition_elements.edition import Edition
from .edition_elements.name import Name
from .edition_elements.pers_name import PersName
from .edition_elements.g import G
from .edition_elements.num import Num
from .edition_elements.role_name import RoleName
from .edition_elements.expan import Expan
from .edition_elements.w import W
from .enums import (
    SpaceUnit,
    AbbrType,
    DoNotPrettifyChildren
)


class EpiDoc(TeiDoc):

    """
    This class provides services for interacting with individual
    EpiDoc files.
    It is therefore the domain of metadata such as 
    date, authority etc.
    as well as that for accessing the editions present
    in the file.
    """
    
    def __init__(
            self, 
            inpt: Path | BytesIO | str | _ElementTree | XmlElement,
            validate_on_load: bool=False,
            verbose: bool=True):
        
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
        self.assert_has_tei_ns()

        if validate_on_load:
            validation_result, msg = self.validate()
            
            if not validation_result:
                raise EpiDocValidationError(msg)
            
            if verbose:
                print(f'{self._p} is a valid EpiDoc file')

    def __repr__(self) -> str:
        return f'EpiDoc(id="{self.id}")'

    def __eq__(self, other) -> bool:
        if not isinstance(other, EpiDoc):
            raise TypeError(f'Cannot compare type EpiDoc with {type(other)}')
        
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def abs(self) -> list[Ab]:
        return list(chain(*[edition.abs 
                            for edition in self.editions()]))

    @property
    def apparatus(self) -> list[_Element]:
        return self.get_div_descendants_by_type('apparatus')
        
    def assert_has_tei_ns(self) -> bool:
        """
        Return True if uses TEI namespaces;
        raises an AssertionError if not
        """
        if self.e is None:
            raise TypeError("No root element present")
        
        nsmap: dict[str, str] = self.e.nsmap

        if nsmap is None:
             raise TEINSError("No namespaces are specified")

        if not 'http://www.tei-c.org/ns/1.0' in nsmap.values():
            raise TEINSError("TEI namespace is not present in the nsmap")
        
        return True

    @property
    def body(self) -> Body:

        """
        Return the body element of the XML file
        as a `Body` object.
        """
        
        body = maxone(self.get_desc(['body']))

        if body is None:
            raise ValueError('No body element found.')
        
        return Body(body)

    @property
    def commentary(self) -> list[_Element]:
        return self.get_div_descendants_by_type('commentary')

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
        Converts all <w> to <name> in the main edition, in place, if they 
        begin with a capital.
        """
        
        if self.main_edition is None:
            raise ValueError('No main edition. Not converting <w> to <name>.')

        self.main_edition.convert_ws_to_names()
        
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
    def daterange(self) -> tuple[Optional[int], Optional[int]]:
        """
        Return a pair (not_before, not_after). If the document
        has a single date, the pair (date, date) is a returned.
        """

        _daterange = (self.not_before, self.not_after)

        if _daterange == (None, None):
            return (self.date, self.date)
        
        return _daterange
        
    @property
    def date_mean(self) -> Optional[int]:
        """
        Return a single date for the document.
        If the document has a single `date`, this is
        returned. Otherwise the mean date is returned,
        calculated by summing the `not_before` and 
        `not_after` property and dividing by two, returning
        as an `int`.
        """

        if self.date is not None:
            return self.date

        not_before, not_after = self.daterange
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
            .get_desc_tei_elems('distributor'), 
        )

        if elem is None:
            return None
        
        return elem.text

    @property
    def div_langs(self) -> set[str]:

        """
        Used by I.Sicily to host language information.
        """
        
        textpart_langs = [textpart.lang 
            for edition in self.editions()
                for textpart in edition.textparts
                    if textpart.lang is not None]

        edition_langs = [edition.lang for edition in self.editions()
            if edition.lang is not None]

        combined = textpart_langs + edition_langs

        return set(combined)

    @property
    def edition_main(self) -> Edition | None:
        
        """
        Return the main edition (i.e. not transliteration or
        lemmatized edition).

        If the @subtype attribute is set to 'unsupplied',
        this is currently treated as though the 
        main edition is not present, and None is returned.
        """
        try:
            return self.body.edition_by_subtype(subtype=None) or \
                self.body.edition_by_subtype(subtype='PHI') or \
                self.body.edition_by_subtype(subtype='EDR')
        except ValueError as e:
            raise ValueError(f"Encountered the following error in {self.id}:\n"
                             f"{e.args[0]}")

    def edition_by_subtype(self, subtype: str | None) -> Edition | None:
        
        """
        Return an edition according to the subtype given in the 
        subtype parameter, if it exists; else None. 

        :param subtype: the subtype of the edition to be found.
        If None, attempts to return the main edition.
        """

        return self.body.edition_by_subtype(subtype)
    
    @property
    def _edition_subtypes(self) -> list[str]:
        """
        Return a list of edition subtype strings. For 
        establishing which subtypes exist on the corpus.
        """

        return remove_none([edition.get_attrib('subtype') 
                for edition in self.editions(include_transliterations=True)
                ])

    def editions(self, include_transliterations=False) -> list[Edition]:

        """
        Return a list of Edition elements
        """

        return self.body.editions(include_transliterations)

    def ensure_lemmatized_edition(
            self, 
            resp: RespStmt | None = None,
            change: Change | None = None
            ) -> Edition:

        """
        Ensures a `simple-lemmatized` edition exists, ready to contain
        lemmatized elements, but no words are copied
        or lemmatized.
        Returns either the existing `simple-lemmatized` edition, or
        an empty one if one already exists.
        """

        # Check no lemmatized editions already
        lemmatized_edition = self.body.edition_by_subtype('simple-lemmatized')
        if lemmatized_edition is not None:
            return lemmatized_edition

        # Create edition if it does not already exist
        self.body.append_new_edition('simple-lemmatized', resp=resp)
        if change is not None: 
            self.append_change(change)
        edition = self.body.edition_by_subtype('simple-lemmatized')

        # Raise an error if could not be created
        if edition is None:
            raise TypeError('Failed to create a simple lemmatized edition.')
        
        return edition

    def ensure_tei_header(self) -> TeiHeader:
        if self.tei_header is None:
            self._append_new_tei_header()
        assert self.tei_header is not None
        return self.tei_header

    @property
    def expans(self) -> list[Expan]:
        """
        Returns a list of abbreviated items (including both 
        abbreviation and expansion)
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
    def file_desc(self) -> FileDesc | None:
        tei_header = self.tei_header
        if tei_header is None: 
            return None
        return tei_header.file_desc

    @property
    def first_edition(self) -> Optional[Edition]:
        """
        Return the first edition in the document,
        regardless of its type
        """
        return self.editions(True)[0] if self.editions(True) != [] else None

    @property
    def formatted_text(self) -> str:
        _text = '\n'.join([edition.formatted_text 
                           for edition in self.editions()])
        return f'\n{self.id}\n{len(self.id) * "-"}\n{_text}\n'

    @property
    def forms(self) -> set[str]:
        return set([str(word) for word in self.tokens_no_nested])

    @property
    def gs(self) -> list[G]:

        """
        Return a list of <g> (= divider) elements
        """

        edition = self.editions()[0]
        if edition is None:
            return []
        
        gs = map(G, edition.get_desc('g'))
        return list(gs)

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

    def get_textclasses(
            self, 
            throw_if_more_than_one: bool) -> list[str]:
        """
        Returns a list of text classes in the document

        :param throw_if_more_than_one: if True, throws an error if 
        more than one <textClass> element is present (as appears to be 
        the case if IRCyr, where the first element is empty). 
        If False, returns the results from the last <textClass> 
        element.
        """
        try:
            textclass_elems = self.get_desc('textClass')
            textclass_e = maxone(
                self.get_desc('textClass'), 
                throw_if_more_than_one=throw_if_more_than_one,
                idx=len(textclass_elems) - 1)
            
        except ValueError as e:
            raise ValueError(f'Could not return a textClass from {self.id}. '
                             'This is likely because the element was either '
                             'not present, or because there were more than one.')

        if textclass_e is None:
            return []

        textclass_element = EpiDocElement(textclass_e)

        terms = textclass_element.get_desc_tei_elems('term')
        terms_with_ana = [term for term in terms 
                                if term.has_attrib('ana')]

        functions = []
        for term in terms_with_ana:
            ana_term = term.get_attrib('ana')

            if ana_term is not None:
                functions += ana_term.split()

        return functions

    @property
    def has_no_main_edition(self) -> bool:
        return self.main_edition is None or \
            self.main_edition.is_empty or \
            self.edition_by_subtype('unsupplied') is not None

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
        The document ID, e.g. ISic000001
        """

        def get_idno_elems(s: str) -> list[XmlElement]:
            if self.publication_stmt is None:
                return []

            return self.publication_stmt.get_desc_tei_elems('idno', {'type': s})            

        id_sources = {
            'Epigraphische Datenbank Heidelberg': 'localID',
            'I.Sicily': 'filename',
            'Università di Bologna': 'localID',
            'King’s College London': 'filename',
            "Centre for Computing in the Humanities, King's College London": 'filename'
        }

        if self.authority is None:
            return 'None'
        
        source = id_sources.get(self.authority, 'filename')

        if source is None:
            return 'None'
        
        idno_elems = get_idno_elems(s=source)
        idno_elem = maxone(idno_elems)

        if idno_elem is None:
            return 'None'

        return idno_elem.text or ''

    @property
    def id_carriers(self) -> list[EpiDocElement]:
        return list(chain(*[edition.local_idable_elements 
                            for edition in self.editions()]))

    def insert_w_inside_name_and_num(self) -> EpiDoc:
        """
        Enclose contents of <name> and <num> tags in <w> tag,
        in place for all editions. By default does nothing if already contains a <w> 
        element.
        """

        for edition in self.editions(True):
            edition.insert_ws_inside_named_entities()

        return self

    def is_after(self, start: int) -> bool:
        """
        Return True if either @notBefore is greater than 
        `end` or @date is greater than `end`
        """

        if self.not_before is not None and self.not_before >= start:
            return True
        
        if self.date is not None and self.date >= start:
            return True
        
        return False

    def is_before(self, end: int) -> bool:
        """
        Return True if either @notAfter is less than `end`
        or @date is less than `end`.
        """

        if self.not_after is not None and self.not_after <= end:
            return True
        
        if self.date is not None and self.date <= end:
            return True
        
        return False
    
    @property
    def is_lemmatizable(self) -> bool:
        return self.tokens_no_nested.__len__() > 0

    @property
    def is_multilingual(self) -> bool:
        return len(self.div_langs) > 1 or len(self.langs) > 1

    def _get_daterange_attrib(self, attrib_name: str) -> Optional[int]:
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

        languages = lang_usage.get_desc_tei_elems('language')
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
    
    @cached_property
    def leiden_text(self) -> str:
        """
        Return the Leiden-formatted text of the inscriptions.
        Alias for `text_leiden` property.
        """
        return self.text_leiden

    def lemmatize(
            self, 
            lemmatize: Callable[[str], str],
            where: Literal['main', 'separate'],
            resp_stmt: RespStmt | None = None,
            change: Change | None = None,
            verbose = False,
            fail_if_existing_lemmatized_edition: bool = True
        ) -> EpiDoc:

        """
        Lemmatize all the <w> elements in 
        the EpiDoc document.

        :param lemmatize: a function with one parameter,
        the form needing lemmatization, returning the 
        lemma.

        :param where: where to put the lemmatized version,
        either on a separate <div> or on the main <div>. 
        If a separate edition is not present, one is created 
        containing copies of the elements that need lemmatizing.

        :param fail_if_existing_lemmatized_edition: Raise exception
        if a lemmatized edition is already present.
        """

        # Check there is a main edition
        main_edition = self.edition_by_subtype(None)
        if main_edition is None:
            raise ValueError('No main edition could be found.')

        if where == 'separate':
            # Create a separate lemmatized edition if not already present
            lemmatized_edition = self.edition_by_subtype('simple-lemmatized') 

            # Check what should do if a lemmatized edition is already present
            if lemmatized_edition and fail_if_existing_lemmatized_edition:
                raise ValueError('A lemmatized edition is already present; PyEpiDoc is '
                                 'currently set to stop if this is the case.')
            elif lemmatized_edition is None:
                lemmatized_edition = self.ensure_lemmatized_edition(resp=resp_stmt)
                self.body.copy_lemmatizable_to_lemmatized_edition(
                    source=main_edition, 
                    target=lemmatized_edition
                )

            edition = lemmatized_edition

        elif where == 'main':
            edition = main_edition
        else:
            raise TypeError(
                f'Invalid destination for lemmatized items: {where}')

        for w in edition.w_tokens:
            w.lemma = lemmatize(w.normalized_form or '')
        
        if resp_stmt:
            self.append_resp_stmt(resp_stmt)

        if change:
            self.append_change(change)

        self.prettify(prettifier='pyepidoc', verbose=verbose)
        
        return self
    
    @property
    def local_idable_elements(self) -> list[EpiDocElement]:

        """
        Get all the tokens in the main edition that should 
        receive an `@n` id.
        """

        if self.edition_main is None:
            raise ValueError('No main edition. Cannot extract n_id elements.')

        return self.edition_main.local_idable_elements

    @property
    def main_edition(self) -> Edition | None:
        """
        Return the main edition of the document, i.e. not
        the transliteration or the lemmatized editions
        """

        return self.edition_main

    @property
    def mainlang(self) -> Optional[str]:
        if self.textlang is None:
            return None
        return self.textlang.get_attrib('mainLang')

    @property
    def mean_date(self) -> int | None:
        return self.date_mean

    @property
    def lemmata(self) -> set[str]:
        _lemmata = [word.lemma for word in self.tokens_no_nested 
            if word.lemma is not None]

        return set(_lemmata)

    @property
    def materialclasses(self) -> list[str]:

        material_e = self.get_desc('material')
        
        if material_e is None:
            return []
        
        return remove_none([EpiDocElement(e).get_attrib('ana') 
                            for e in material_e])

    def names(self, 
              predicate: Callable[[Name], bool] = lambda _: True
              ) -> list[Name]:
        """
        Return a list of `Name` objects for all the
        <name> elements in the document's main edition.

        :param name_predicate: a function containing
        a condition for whether or not to include a name.
        Defaults to returning True.
        """

        edition = self.main_edition
        if edition is None:
            return []
        
        names = filter(predicate, map(Name, edition.get_desc('name')))
        return list(names)



    @property
    def nums(self) -> list[Num]:
        edition = self.editions()[0]
        if edition is None:
            return []
        
        nums = map(Num, edition.get_desc('num'))
        return list(nums)

    @property
    def not_after(self) -> Optional[int]:
        """
        Return the value of the @notAfter or @notAfter-custom attribute,
        whichever is present
        """
        not_after_custom = self._get_daterange_attrib('notAfter-custom')
        not_after = self._get_daterange_attrib('notAfter')
        return not_after_custom or not_after

    @property
    def not_before(self) -> Optional[int]:
        """
        Return the value of the @notBefore or @notBefore-custom attribute,
        whichever is present
        """
        not_before_custom = self._get_daterange_attrib('notBefore-custom')
        not_before = self._get_daterange_attrib('notBefore')
        return not_before_custom or not_before

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
    def otherlangs(self) -> list[str]:
        if self.textlang is None:
            return []
        
        otherlangs = self.textlang.get_attrib('otherLangs')
        
        if otherlangs is None:
            return []

        return otherlangs.split()

    @property
    def pers_names(self) -> list[PersName]:

        """
        Return a list of <persName> elements wrapped in
        PersName objects.
        """

        if self.editions() == []:
            return []
        
        pers_name_elems = (self
            .editions()[0]
            .get_desc_tei_elems('persName')
        )
        
        pers_names = map(
            lambda elem: PersName(elem.e), 
            pers_name_elems
        )
    
        return list(pers_names)

    @property
    def prefix(self) -> str:
        if self.authority == "I.Sicily":
            return "ISic"
        elif self.authority == "Epigraphische Datenbank Heidelberg":
            return "HD"
        
        return ""

    def prettify(
            self, 
            prettifier: Literal['pyepidoc'] = 'pyepidoc',
            prettify_main_edition: bool = True,
            verbose = False) -> EpiDoc:

        """
        Use prettify function in `lxml` to prettify the whole document.

        :param prettifier: 'lxml' uses the prettifier in lxml. Note
        that this will deep copy the epidoc file. 'pyepidoc' uses 
        the internal prettifier, which does not deep copy the file.

        :param prettify_main_edition: If True, aligns the main edition
        on <lb> elements.
        """

        if prettifier == 'lxml':
            # self = self._prettify_with_lxml()
            raise NotImplementedError()

        elif prettifier == 'pyepidoc':

            self._prettify_with_pyepidoc(SpaceUnit.Space.value, 4)
    
        else:
            raise TypeError('Prettifier must either be '
                            'lxml or pyepidoc.')

        if prettify_main_edition:
            self.prettify_main_edition(SpaceUnit.Space.value, 4, verbose=verbose)

        return self

    def _prettify_with_lxml(self) -> EpiDoc:

        """
        Use the prettifier in `lxml` to prettify the 
        xml file. Deepcopies the file.
        """

        prettified_str: bytes = etree.tostring(
            element_or_tree=self.e,
            xml_declaration=True, # type: ignore
            pretty_print=True # type: ignore
        )
        
        parser = etree.XMLParser(
            load_dtd=False,
            resolve_entities=False,
            remove_blank_text=True,
        )
        root_elem: _Element = etree.fromstring(
            text=prettified_str, 
            parser=parser
        )

        tree = root_elem.getroottree()
        prettified_doc = EpiDoc(tree)

        return prettified_doc
    
    def _prettify_with_pyepidoc(
            self, 
            space_unit: str,
            multiplier: int = 4) -> EpiDoc:
        """
        Use pyepidoc's internal prettifier to prettify the document.
        """

        epidoc = self
        epidoc.desc_elems
        elem = XmlElement(epidoc.e)
        elem.prettify_element_with_pyepidoc(
            space_unit, 
            multiplier, 
            exclude=DoNotPrettifyChildren.values()
        )
        
        # Root element
        # Remove trailing text
        self.root_elem.tail = ''
        self.root_elem.text = '\n' + multiplier * space_unit + (self.root_elem.text or '').strip() \
            if len(self.desc_elems) > 0 \
            else '\n' + space_unit * multiplier + (self.root_elem.text or '').strip()
        
        return epidoc

    def prettify_main_edition(
        self, 
        spaceunit = SpaceUnit.Space.value, 
        number = 4, 
        verbose = True
    ) -> None:

        """
        Prettify the xml of the <div type="edition"> element; this
        cannot be done automatically using lxml since this element
        will have @xml:space="preserve".

        :param replace_tabs: If True, replaces all tab characters with 
        the correct multiple of spaceunit.
        """
    
        if verbose: 
            print(f'Prettifying {self.id}...')

        if self.main_edition is not None:
            self.main_edition.prettify(spaceunit, number)

    def print_leiden(self) -> None:
        """
        Print Leiden text to stdout
        """
        print(self.leiden_text)

    def print_translation(self) -> None:
        """
        Print translation text to stdout
        """
        print(self.translation_text)

    @property
    def publication_stmt(self) -> Optional[EpiDocElement]:
        publication_stmt = maxone(self.get_desc('publicationStmt'))
        if publication_stmt is None:
            return None
        return EpiDocElement(publication_stmt)
    
    @property
    def _pyepidoc_module_path(self) -> Path:
        
        """
        Returns the path of the pyepidoc module.
        Indended for use with obtaining the path 
        of the rng validation file.
        """

        return Path(inspect.getfile(pyepidoc))
    
    @property
    def _rng_path(self) -> Path:
        """
        Returns the path of the 'tei-epidoc.rng' file
        for use in validation.
        """
        return Path(self._pyepidoc_module_path).parent.parent / Path('pyepidoc_data/schemas/tei-epidoc.rng')

    @property
    def role_names(self) -> list[RoleName]:
        """
        Return a list of RoleName objects for each 
        <roleName> in the edition.
        If there is no edition, returns an empty list.  
        """

        if self.editions() == []:
            return []
        
        role_name_elems = (self
            .editions()[0]
            .get_desc_tei_elems('roleName')
        )
        
        role_names = map(
            lambda elem: RoleName(elem.e), 
            role_name_elems
        )
    
        return list(role_names)

    def set_ids(self, base: Base=100) -> None:
        
        """
        Put @xml:id on all elements of the edition,
        in place. There are two options, using either
        Base 52 or Base 100. Should keep any id that 
        already exist on an element.
        """
        # TODO remove this method

        for edition in self.editions():
            edition.set_ids(base)

    def set_full_ids(self, base: Base=100) -> None:
        """
        Put @xml:id on all elements of the edition,
        in place. There are two options, using either
        Base 52 or Base 100. Should keep any id that 
        already exist on an element.
        """

        self.set_ids(base)

    def set_local_ids(self, interval: int = 5) -> EpiDoc:
        
        """
        Put @n on certain elements in the edition

        :param interval: the interval between ids, e.g. 
        with 5, it will be 5, 10, 15, 20 etc.
        """

        if self.main_edition is None:
            raise ValueError('No main edition found to set'
                             '@n ids on.')
        
        self.main_edition.set_local_ids(interval=interval)
        return self

    @property
    def simple_lemmatized_edition(self) -> Edition | None:
        """
        Return the 'simple-lemmatized' edition, if it exists,
        or None if not.
        """

        return self.body.edition_by_subtype('simple-lemmatized')

    def space_tokens(self) -> None:
        for edition in self.editions():
            edition.space_tokens()

    @property
    def supplied(self) -> list[XmlElement]:
        return list(chain(*[edition.supplied for edition in self.editions()]))

    @property
    def tei(self) -> Optional[_Element]:
        """
        Return the `<TEI>` root element
        """
        return maxone(self.get_desc('TEI'))

    @property
    def tei_header(self) -> Optional[TeiHeader]:
        tei_header_elem = maxone(self.root_elem.get_desc_tei_elems('teiHeader'))
        if tei_header_elem is None:
            return None
        
        return TeiHeader(tei_header_elem)

    def text(self, type: Literal['leiden', 'normalized', 'xml']) -> str:
        
        """
        :param type: the type of text wanted, whether
        the Leiden version or a normalized version (i.e. with all the 
        abbreviations expanded), or the raw text content of the descendant
        XML nodes
        :return: the edition text of the document
        """
        leiden_editions = [edition.get_text(type) 
                        for edition in self.editions()]
        
        return '\n'.join(leiden_editions)    

    @property
    def text_elems(self) -> list[EpiDocElement]:
        """
        All elements in the document responsible for carrying
        text information as part of the edition
        """
        elems = chain(*[ab.descendant_elements for ab in self.abs])
        return list(map(EpiDocElement, elems))

    @cached_property
    def text_leiden(self) -> str:
        """
        :return: a string containing the Leiden representation of the
        document including line breaks
        """

        return self.text('leiden')

    @property
    def text_normalized(self) -> str:
        """
        :return: a normalized version of the edition text (i.e.
        all abbreviations expanded etc.) with no line breaks
        """
        return self.text('normalized')
    
    @property
    def text_xml(self) -> str:

        """
        Raw text from XML nodes
        """

        return self.text('xml')

    @property
    def textclasses(self) -> list[str]:
        """
        Returns textclass information from the <textClass> element.
        At the moment PyEpiDoc assumes that the relevant 
        information is stored under one or more <term> elements, in the @ana
        attribute. It also assumes there is only
        one <textClass> element. If this last assumption is not 
        valid (as appears to be the case currently for IRCyr),
        please use the _get_textclasses method directly, with 
        the `throw_if_more_than_one` parameter set to False. 
        """

        return self.get_textclasses(True)

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
    
    @property
    def texttype(self) -> str | None:
        """
        Used by IRCyr to store text type (text class) 
        information
        """

        elem = maxone([desc for desc in self.desc_elems
                if desc.localname == 'rs' and desc.get_attrib('type') == 'textType'],
                throw_if_more_than_one=False)
        
        if elem is None:
            return None
        else:
            return EpiDocElement(elem).text
        
    @property
    def title_stmt(self) -> TitleStmt | None:
        """
        The <titleStmt> element of the document,
        providing details including a series of 
        <respStmt>
        """
        if self.file_desc is None:
            return None
        return self.file_desc.title_stmt

    @overload   
    def to_xml_file(
        self, 
        dst: Path, 
        verbose=True,
        collapse_empty_elements = False,
        overwrite_existing = False
    ) -> None:
        
        ...

    @overload
    def to_xml_file(
        self,
        dst: str,
        verbose = True,
        collapse_empty_elements = False,
        overwrite_existing = False
    ) -> None:
        
        ...

    def to_xml_file(
        self, 
        dst: Path | str, 
        verbose = True,
        collapse_empty_elements = False,
        overwrite_existing = False
    ) -> None:
        
        """
        Writes out the XML to file
        """
        if isinstance(dst, Path):
            p = dst
        else:
            p = Path(dst)

        if not p.parent.exists():
            raise FileExistsError(
                f'Directory {p.parent.absolute()} does not exist.'
            )

        if verbose: 
            print(f'Writing {self.id}...')

        if overwrite_existing:
            mode = 'wb'
        else:
            mode = 'xb'
        
        with open(dst, mode=mode) as f:
            f.write(self.to_byte_str(collapse_empty_elements))

    def to_xml_file_object(self, collapse_empty_elements: bool = False) -> io.BytesIO:
        """
        Write the file to a file object in memory, rather than
        to a file on disk
        """
        return io.BytesIO(self.to_byte_str(collapse_empty_elements))

    @property
    def token_count(self) -> int:
        return len(self.tokens_no_nested)

    def tokenize(
            self, 
            add_space_between_words: bool = True,
            prettify_edition: bool = True,
            set_universal_ids: bool = False,
            set_n_ids: bool = False,
            convert_ws_to_names: bool = False,
            verbose: bool = True,
            insert_ws_inside_named_entities: bool = False,
            throw_if_no_main_edition: bool = True,
            retokenize: bool = True
        ) -> EpiDoc:
        
        """
        Tokenizes the EpiDoc document, in place.

        :param add_space_between_words: if True, adds a space
        between token elements
        :param prettify_edition: if True, prettify the <div type="edition"> element (overriding xml:space="preserve")
        :param set_ids: sets full ids on the tokenized elements
        :param convert_ws_to_names: attempts to convert <w> elements to <name>
        on the basis of capital letters
        :param verbose: If True, prints a message with the id of the file that is being tokenized.
        :param insert_ws_inside_names_and_nums: If True, inserts <w> tag inside <name> and <num> tags
        :param throw_if_no_main_edition: Throw an error if there is no main edition
        :param retokenize: Redo the tokenization if there are already <w> tokens presentt
        """

        if verbose: 
            print(f'Tokenizing {self.id}...')

        if self.main_edition is None:
            if throw_if_no_main_edition:
                raise ValueError(f'No main edition to tokenize in {self.id}.')
            else:
                return self
        
        if len(self.w_tokens) == 0 or retokenize:
            self.main_edition.tokenize()
        else:
            print(f'Did not tokenize {self.id} because already contains <w> elements.')

        if add_space_between_words:
            self.space_tokens()
        
        if convert_ws_to_names:
            self.convert_ws_to_names()

        if insert_ws_inside_named_entities:
            self.main_edition.insert_ws_inside_named_entities()

        if set_universal_ids:
            self.set_ids(base=100)

        if set_n_ids:
            self.set_local_ids()
            
        if prettify_edition:
            self.prettify_main_edition(
                spaceunit=SpaceUnit.Space.value, 
                number=4,
                verbose=verbose
            )

        return self

    @property
    def tokens(self) -> list[Token]:
        """
        :return: a list of all the tokens in the document, 
        excluding tokens within tokens
        """
        return self.tokens_no_nested

    @property
    def tokens_incl_nested(self) -> list[Token]:
        """
        :return: a list of all the tokens in the document, 
        including tokens within tokens
        """
        tokens = chain(*[edition.tokens_incl_nested 
                         for edition in self.editions()])
        return list(tokens)        

    @property
    def tokens_as_strings(self) -> list[str]:
        """
        :return: tokens as a list of strings
        """
        return [str(token) for token in self.tokens]

    @property
    def tokens_no_nested(self) -> list[Token]:
        """
        :return: a list of all the tokens in the document, 
        excluding tokens within tokens
        """
        tokens = chain(*[edition.tokens_no_nested 
                         for edition in self.editions()])
        return list(tokens)
        
    @property
    def tokens_normalized_no_nested(self) -> list[Token]:

        """
        Returns list of tokens of the <div type="edition">.
        If the normalised form is an empty string,
        does not include the token.
        """

        return list(chain(*[edition.tokens_normalized_no_nested
                            for edition in self.editions()]))

    @property
    def translation_text(self) -> str:
        """
        :return: the text for all translations, if present
        """
        
        translation_divs = self.get_div_descendants_by_type('translation')

        return '\n'.join([EpiDocElement(div).text_desc_compressed_whitespace 
                       for div in translation_divs])
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate according to the TEI EpiDoc RelaxNG schema

        :return: a validation result as a bool, and a string giving a validation
        message, either an error if it has failed, or a string 
        confirming that the file is valid.
        """
        return self.validate_by_relaxng(self._rng_path)
    
    @property
    def w_tokens(self) -> list[Token]:
        return list(chain(*[edition.w_tokens 
                            for edition in self.editions()]))
    
    @property
    def xml_ids(self) -> list[str]:
        """
        Convenience property for the element @xml:id IDs in the editions of the document
        """

        abs = chain(*[edition.abs 
                      for edition in self.editions()])
        elems = chain(*[ab.id_carriers for ab in abs])

        return [elem.xml_id for elem in elems 
                if elem.xml_id is not None]

