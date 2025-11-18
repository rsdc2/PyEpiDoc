from __future__ import annotations
from typing import (
    Optional, 
    Literal, 
    overload
)

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

import pyepidoc
from pyepidoc.xml.docroot import DocRoot
from pyepidoc.shared import (
    maxone, 
    listfilter, 
    head,
    remove_none
)

from pyepidoc.shared.types import Base
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.shared.enums import SpaceUnit, DoNotPrettifyChildren
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.tei.tei_text import Text

from .tei_body import TeiBody
from .errors import TEINSError
from .metadata.title_stmt import TitleStmt
from .metadata.resp_stmt import RespStmt
from .metadata.file_desc import FileDesc
from .metadata.tei_header import TeiHeader
from .metadata.change import Change


class TeiDoc(DocRoot):

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
            inpt: Path | BytesIO | str | _ElementTree | XmlElement):
        
        """
        Initialize a TeiDoc object on a given input 
        (string, Path or lxml _ElementTree).
        On load checks that the file has the TEI namespace 
        "http://www.tei-c.org/ns/1.0" declared.

        :param inpt: string (containing path to document), 
            Path or lxml _ElementTree
        """
        
        super().__init__(inpt)
        self.assert_has_tei_ns()

    def __repr__(self) -> str:
        return f'TeiDoc(id="{self.id}")'

    def __eq__(self, other) -> bool:
        if not isinstance(other, TeiDoc):
            raise TypeError(f'Cannot compare type EpiDoc with {type(other)}')
        
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def apparatus(self) -> list[_Element]:
        return self.get_div_descendants_by_type('apparatus')
    
    def append_change(self, change: Change) -> TeiDoc:
        self.ensure_tei_header().ensure_revision_desc().append_change(change)
        return self
    
    def _append_new_tei_header(self) -> TeiDoc:
        """
        Insert a <teiHeader> element as the first child
        """
        tei_header_elem = TeiHeader.create()
        self.e.insert(0, tei_header_elem.e)
        return self

    def append_resp_stmt(self, resp_stmt: RespStmt) -> TeiDoc:
        """
        Add a `<respStmt>` element to the `<titleStmt>`. Creates the necessary element  
        hierarchy if not present.
        """

        if self.title_stmt is None:
            if self.file_desc is None:
                if self.tei_header is None:
                    self._append_new_tei_header()
                self.tei_header.append_new_file_desc() #type: ignore
            self.file_desc.append_title_stmt(TeiElement.create('titleStmt')) #type: ignore

        self.title_stmt.append_resp_stmt(resp_stmt) #type: ignore

        return self
    
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
    def authority(self) -> Optional[str]:
        if self.publication_stmt is None:
            return None

        elem = maxone(self
            .publication_stmt
            .get_desc_tei_elems('authority'), 
        )

        if elem is None:
            return None
        
        return elem._e.text

    @property
    def body(self) -> TeiBody:

        """
        Return the body element of the XML file
        as a `Body` object.
        """
        
        body = self.text.body        
        return TeiBody(body)

    @property
    def commentary(self) -> list[_Element]:
        return self.get_div_descendants_by_type('commentary')
    
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
        
        return elem._e.text

    def ensure_tei_header(self) -> TeiHeader:
        if self.tei_header is None:
            self._append_new_tei_header()
        assert self.tei_header is not None
        return self.tei_header
    
    @property
    def file_desc(self) -> FileDesc | None:
        tei_header = self.tei_header
        if tei_header is None: 
            return None
        return tei_header.file_desc

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

        textclass_element = TeiElement(textclass_e)

        terms = textclass_element.get_desc_tei_elems('term')
        terms_with_ana = [term for term in terms 
                                if term._e.has_attrib('ana')]

        functions = []
        for term in terms_with_ana:
            ana_term = term.get_attrib('ana')

            if ana_term is not None:
                functions += ana_term.split()

        return functions

    @property
    def id(self) -> str:

        """
        The document ID, e.g. ISic000001
        """

        def get_idno_elems(s: str) -> list[TeiElement]:
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

    def _get_daterange_attrib(self, attrib_name: str) -> Optional[int]:
        if self.orig_date is None:
            return None

        daterange_val = self.orig_date._e.get_attrib(attrib_name)

        try:
            return int(daterange_val) if daterange_val is not None else None
        except ValueError:
            return None

    @property
    def lang_usages(self) -> list[str]:

        """Used by EDH to host language information."""

        language_elems = [TeiElement(language) 
                          for language in self.get_desc('langUsage')]
        lang_usage = maxone(language_elems, None)

        if lang_usage is None: 
            return []

        languages = lang_usage.get_desc_tei_elems('language')
        idents = [language._e.get_attrib('ident') for language in languages]
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
        return self.textlang._e.get_attrib('mainLang')

    @property
    def mean_date(self) -> int | None:
        return self.date_mean

    @property
    def materialclasses(self) -> list[str]:

        material_e = self.get_desc('material')
        
        if material_e is None:
            return []
        
        return remove_none([TeiElement(e)._e.get_attrib('ana') 
                            for e in material_e])

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
    def orig_date(self) -> Optional[TeiElement]:
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
                TeiElement(orig_date)._e.get_desc('origDate'), 
                throw_if_more_than_one=False
            )    

        if orig_date is None:
            return None        

        return TeiElement(orig_date)
 
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
    def prefix(self) -> str:
        if self.authority == "I.Sicily":
            return "ISic"
        elif self.authority == "Epigraphische Datenbank Heidelberg":
            return "HD"
        
        return ""

    def prettify(
            self, 
            prettifier: Literal['pyepidoc'] = 'pyepidoc'
            ) -> TeiDoc:

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

        return self

    def _prettify_with_lxml(self) -> TeiDoc:

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
        prettified_doc = TeiDoc(tree)

        return prettified_doc
    
    def _prettify_with_pyepidoc(
            self, 
            space_unit: str,
            multiplier: int = 4) -> TeiDoc:
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

    def print_translation(self) -> None:
        """
        Print translation text to stdout
        """
        print(self.translation_text)

    @property
    def publication_stmt(self) -> Optional[TeiElement]:
        publication_stmt = maxone(self.get_desc('publicationStmt'))
        if publication_stmt is None:
            return None
        return TeiElement(publication_stmt)
    
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
    def tei(self) -> Optional[_Element]:
        """
        Return the `<TEI>` root element
        """
        return maxone(self.get_desc('TEI'))

    @property
    def tei_header(self) -> Optional[TeiHeader]:
        root = TeiElement(self)
        tei_header_elem = maxone(root.get_desc_tei_elems('teiHeader'))
        if tei_header_elem is None:
            return None
        
        return TeiHeader(tei_header_elem)  

    @property
    def text(self) -> Text:
        text = self.root_elem.child_element_by_local_name('text')
        return Text(text)

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
    def textlang(self) -> Optional[TeiElement]:
        """
        Used by I.Sicily to host language information.        
        """

        textlang = maxone([TeiElement(textlang) 
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
            return TeiElement(elem).text
        
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
    def translation_text(self) -> str:
        """
        :return: the text for all translations, if present
        """
        
        translation_divs = self.get_div_descendants_by_type('translation')

        return '\n'.join([TeiElement(div)._e.text_desc_compressed_whitespace 
                       for div in translation_divs])
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate according to the TEI EpiDoc RelaxNG schema

        :return: a validation result as a bool, and a string giving a validation
        message, either an error if it has failed, or a string 
        confirming that the file is valid.
        """
        return self.validate_by_relaxng(self._rng_path)

