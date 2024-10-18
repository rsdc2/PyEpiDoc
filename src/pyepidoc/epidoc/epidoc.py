from __future__ import annotations
from typing import (
    Optional, 
    Literal, 
    overload,
    Callable
)

from lxml import etree
from lxml.etree import (
    _Element, 
    _ElementTree
)

from pathlib import Path
from itertools import chain
import inspect
import re

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
from .element import EpiDocElement, BaseElement

from .elements.ab import Ab
from .elements.body import Body
from .elements.edition import Edition
from .elements.name import Name
from .elements.pers_name import PersName
from .elements.g import G
from .elements.num import Num
from .elements.role_name import RoleName
from .elements.expan import Expan
from .elements.w import W
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
    
    def __init__(
            self, 
            inpt: Path | str | _ElementTree,
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
        self.assert_has_TEIns()

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
        Converts all <w> to <name> in place if they 
        begin with a capital.
        """
        
        for edition in self.editions():
            edition.convert_words_to_names()
        
        return self
    
    def _create_lemmatized_edition(self) -> Edition:

        """
        Add a new edition to the document, ready to contain
        lemmatized elements, but no words are copied
        or lemmatized.
        Raises an error if the edition already exists, or
        if the edition could not be created.
        """

        # Check no lemmatized editions already
        lemmatized_edition = self.body.edition_by_subtype('simple-lemmatized')
        if lemmatized_edition is not None:
            raise ValueError('Lemmatized edition already present.')

        # Create edition if it does not already exist
        self.body.create_edition('simple-lemmatized')
        edition = self.body.edition_by_subtype('simple-lemmatized')

        # Raise an error if could not be created
        if edition is None:
            raise TypeError('Failed to create a simple lemmatized edition.')
        
        return edition

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
        """
        
        return self.body.edition_by_subtype(subtype=None)

    def edition_by_subtype(self, subtype: str | None) -> Edition | None:
        
        """
        Return an edition according to the subtype given in the 
        subtype parameter, if it exists; else None. 

        :param subtype: the subtype of the edition to be found.
        If None, attempts to return the main edition.
        """

        return self.body.edition_by_subtype(subtype)

    def editions(self, include_transliterations=False) -> list[Edition]:

        """
        Return a list of Edition elements
        """

        return self.body.editions(include_transliterations)

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
    def first_edition(self) -> Optional[Edition]:
        return self.editions()[0] if self.editions != [] else None

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
    
    def lemmatize(
            self, 
            lemmatize: Callable[[str], str],
            where: Literal['main', 'separate']
        ):

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
        """

        main_edition = self.edition_by_subtype(None)
        if main_edition is None:
            raise ValueError('No main edition could be found.')

        if where == 'separate':
            # Create a separate lemmatized edition if not already
            # present
            lemmatized_edition = self.edition_by_subtype('simple-lemmatized') 
            if lemmatized_edition is None:
                
                lemmatized_edition = self._create_lemmatized_edition()
                self.body.copy_edition_items_to_appear_in_lemmatized_edition(
                    main_edition, 
                    lemmatized_edition
                )

            edition = lemmatized_edition

        elif where == 'main':
            edition = main_edition
        else:
            raise TypeError(
                f'Invalid destination for lemmatized items: {where}')

        for w in edition.w_tokens:
            w.lemma = lemmatize(w.text)
        
        self.prettify(prettifier='pyepidoc')

    @property
    def lemmatized_edition(self) -> Edition | None:
        """
        Return the 'simple-lemmatized' edition, if it exists,
        or None if not.
        """

        return self.body.edition_by_subtype('simple-lemmatized')

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

    @property
    def names(self) -> list[Name]:
        edition = self.editions()[0]
        if edition is None:
            return []
        
        names = map(Name, edition.get_desc('name'))
        return list(names)

    @property
    def n_id_elements(self) -> list[EpiDocElement]:

        """
        Get all the tokens in the main edition that should 
        receive an `@n` id.
        """

        if self.edition_main is None:
            raise ValueError('No main edition. Cannot extract n_id elements.')

        return self.edition_main.n_id_elements

    @property
    def nums(self) -> list[Num]:
        edition = self.editions()[0]
        if edition is None:
            return []
        
        nums = map(Num, edition.get_desc('num'))
        return list(nums)

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
            .get_desc_elems_by_name('persName')
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
            prettifier: Literal['lxml', 'pyepidoc'],
            prettify_main_edition: bool = True) -> EpiDoc:

        """
        Use prettify function in `lxml` to prettify the whole document.

        :param prettifier: 'lxml' uses the prettifier in lxml. Note
        that this will deep copy the epidoc file. 'pyepidoc' uses 
        the internal prettifier, which does not deep copy the file.

        :param prettify_main_edition: If True, aligns the main edition
        on <lb> elements.
        """

        if prettifier == 'lxml':
            self = self._prettify_with_lxml()

        elif prettifier == 'pyepidoc':

            self._prettify_with_pyepidoc(SpaceUnit.Space.value, 4)
    
        else:
            raise TypeError('Prettifier must either be '
                            'lxml or pyepidoc.')

        if prettify_main_edition:
            self.prettify_main_edition(SpaceUnit.Space, 4)

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
            remove_blank_text=True
        )
        tree: _ElementTree = etree.fromstring(
            text=prettified_str, 
            parser=parser
        )

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

        for desc in list(epidoc.desc_elems): 
            
            # Don't touch descdendant nodes containing @xml:space = "preserve"
            if not desc.xmlspace_preserve_in_ancestors:

                # Only insert a new line and tab as first child if there are 
                # child elements
                if len(desc.child_elements) > 0:
                    desc.text = "\n" + \
                        (desc.ancestor_count + 1) * multiplier * space_unit + \
                        desc.text.strip()

                # Add new line and tabs after tag
                if desc.parent is not None and \
                    desc.parent.last_child is not None and \
                        desc.parent.last_child.id_internal == desc.id_internal:
                    
                    # If last child, add one fewer tab so that closing tag
                    # has correct alignment
                    tail_to_append = "\n" + (desc.ancestor_count - 1) * "\t"

                    if desc.tail is None:
                        desc.tail = tail_to_append
                    else:
                        desc.tail = desc.tail.strip() + tail_to_append
                else:
                    desc.tail = "\n" + (desc.ancestor_count) * "\t"

        # Root element
        # Remove trailing text
        self.root_elem.tail = ""
        self.root_elem.text = "\n\t" + self.root_elem.text.strip() \
            if len(self.desc_elems) > 0 \
            else "\n\t" + self.root_elem.text.strip()
        
        return epidoc

    def prettify_main_edition(
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

        if self.main_edition is not None:
            self.main_edition.prettify(spaceunit, number)

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
        return Path(self._pyepidoc_module_path).parent / Path('tei-epidoc.rng')

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
            .get_desc_elems_by_name('roleName')
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

    def set_n_ids(self, interval: int = 5) -> EpiDoc:
        
        """
        Put @n on certain elements in the edition

        :param interval: the interval between ids, e.g. 
        with 5, it will be 5, 10, 15, 20 etc.
        """

        if self.main_edition is None:
            raise ValueError('No main edition found to set'
                             '@n ids on.')
        
        self.main_edition.set_n_ids(interval=interval)
        return self

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

    def text(
            self, 
            type: Literal['leiden', 'normalized', 'xml']) -> str:
        
        """
        :param type: the type of text wanted, whether
        the Leiden version or a normalized version (i.e. with all the 
        abbreviations expanded), or the raw text content of the descendant
        XML nodes
        :return: the edition text of the document
        """
        
        if type == 'leiden':

            leiden = ' '.join([token.leiden_plus_form for token in self.tokens_no_nested])
            
            leiden_ = re.sub(r'\|\s+?\|', '|', leiden)
            leiden__ = re.sub(r'·\s+?·', '·', leiden_)
        
            return leiden__.replace('|', '\n')
        
        elif type == 'normalized':
            tokens = list(chain(*[edition.tokens_normalized_list_str 
                            for edition in self.editions()]))
            return ' '.join(tokens)
        
        elif type == 'xml':
            return '\n'.join(edition.text_desc_compressed_whitespace 
                           for edition in self.editions())

    @property
    def text_elems(self) -> list[EpiDocElement]:
        """
        All elements in the document responsible for carrying
        text information as part of the edition
        """
        elems = chain(*[ab.desc_elems for ab in self.abs])
        return list(map(EpiDocElement, elems))

    @property
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
            raise FileExistsError(
                f'Directory {p.parent.absolute()} does not exist.'
            )

        if verbose: 
            print(f'Writing {self.id}...')
        
        with open(dst, 'w') as f:
            f.write(str(self))

    @property
    def token_count(self) -> int:
        return len(self.tokens_no_nested)

    def tokenize(
        self, 
        add_space_between_words: bool=True,
        prettify_edition: bool=True,
        set_ids: bool=False,
        convert_ws_to_names: bool=False,
        verbose: bool=True
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
            self.prettify_main_edition(spaceunit=SpaceUnit.Space, number=4)

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
    def tokens_list_str(self) -> list[str]:
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
    def tokens_normalized(self) -> list[Token]:

        """
        Returns list of tokens of the <div type="edition">.
        If the normalised form is an empty string,
        does not include the token.
        """

        return list(chain(*[edition.tokens_normalized 
                            for edition in self.editions()]))

    @property
    def translation_text(self) -> str:
        """
        :return: the text for all translations, if present
        """
        
        translation_divs = self.get_div_descendants_by_type('translation')

        return '\n'.join(chain(*[EpiDocElement(div).text_desc_compressed_whitespace 
                       for div in translation_divs]))
    
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
    
