from __future__ import annotations
from typing import (
    Optional, 
    Union, 
    cast, 
    overload, 
    Sequence
)
from pathlib import Path
from copy import deepcopy
from io import BytesIO

from lxml import etree, isoschematron
from lxml.etree import ( 
    _Comment,
    _Element, 
    _ElementTree, 
    _ElementUnicodeResult,
    _ProcessingInstruction,
    XMLSyntaxError, 
    XMLSyntaxAssertionError,
    DocumentInvalid
)

from pyepidoc.shared.constants import TEINS, XMLNS
from pyepidoc.xml.xml_element import XmlElement
from .xml_element import XmlElement
from .errors import handle_xmlsyntaxerror


class DocRoot:  
    _roottree: _ElementTree  
    _e: _Element
    _p: Path
    _valid: Optional[bool] = None

    @overload
    def __init__(self, inpt: XmlElement):
        """
        :param inpt: an lxml _Element tree object representing an
            lxml document
        """
        ...

    @overload
    def __init__(self, inpt: Path):
        """
        :param inpt: Path containing the filepath of the EpiDoc XML file.
        """
        ...

    @overload
    def __init__(self, inpt: BytesIO):
        """
        :param inpt: BytesIO object containing an in-memory version of the file.
        """
        ...

    @overload
    def __init__(self, inpt: str):
        """
        :param inpt: str containing the filepath of the EpiDoc XML file.
        """
        ...

    @overload
    def __init__(self, inpt: _ElementTree):
        """
        :param inpt: an lxml _Element tree object representing an
            lxml document
        """
        ...

    def __init__(self, inpt: Path | BytesIO | str | _ElementTree | _Element | XmlElement):

        if isinstance(inpt, Path):
            self._p = inpt
            if not inpt.exists():
                raise FileExistsError(f'File {inpt.absolute()} does not exist')
            self._e = self._load_e_from_file(inpt)
            return
        
        elif isinstance(inpt, BytesIO):
            self._e = self._load_e_from_file(inpt)
            return
            
        elif isinstance(inpt, _ElementTree):
            self._e = inpt.getroot()
            return

        elif isinstance(inpt, _Element):
            self._e = inpt
            return

        elif isinstance(inpt, XmlElement):
            self._e = inpt._e
            return
        
        elif isinstance(inpt, str):
            self._p = p = Path(inpt)
            if not p.exists():
                raise FileExistsError(f'File {p.absolute()} does not exist')
            self._e = self._load_e_from_file(p)
            return
        
        raise TypeError(f'input is of type {type(inpt)}, but should be either '
                        'Path, _ElementTree, _Element, BaseElement or str.')

    @staticmethod
    def _clean_text(text:str):
        return text.strip()\
            .replace('\n', '')\
            .replace(' ', '')\
            .replace('\t', '')

    def _collapse_empty_elements(self) -> DocRoot:
        """
        Turn a <tag></tag> to <tag/>
        """

        for elem in self.desc_elems:
            if elem.text == '':
                elem.e.text = None

        return self

    @staticmethod
    def _compile_attribs(attribs: Optional[dict[str, str]]) -> str:
        if attribs is None:
            return ''
        return '[' + ''.join([f"@{k}='{attribs[k]}'" for k in attribs]) + ']'

    @property
    def depth(self) -> int:
        return 0

    @property
    def desc_comments(self) -> Sequence[XmlElement]:
        return [XmlElement(item) 
                for item in self._desc_comments]

    @property
    def _desc_comments(self) -> Sequence[_Comment]:
        if self.e is None:
            return []
        
        return [item for item in self.e.iterdescendants(tag=None)
                 if isinstance(item, _Comment)]

    @property
    def desc_elems(self) -> Sequence[XmlElement]:
        if self.e is None:
            return []
        
        return [XmlElement(item) 
                for item in self.e.iterdescendants(tag=None)
                 if isinstance(item, _Element)]

    @property
    def e(self) -> _Element:
        return self._e
    
    @property
    def filename(self) -> str:
        return self._p.stem

    def get_desc(self, 
        elemnames:Union[list[str], str], 
        attribs:Optional[dict[str, str]]=None
    ) -> list[_Element]:

        if self.e is None: 
            return []
        if type(elemnames) is str:
            _elemnames = [elemnames]
        elif type(elemnames) is list:
            _elemnames = elemnames
        else:
            raise TypeError("elemnames has incorrect type.")

        xpathstr = ' | '.join([f'.//ns:{elemname}' + \
                               self._compile_attribs(attribs) 
                               for elemname in _elemnames])

        try:
            xpathRes = (self
                .e
                .xpath(xpathstr, namespaces={'ns': TEINS})
            )
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in get_desc')
            print(e)
            return []
        except XMLSyntaxError as e:
            print('XMLSyntaxError in get_desc')
            handle_xmlsyntaxerror(e)
            return []
        except AssertionError as e:
            print(f'AssertionError in get_desc while analysing {self._p}')
            print(e)
            return []

        if type(xpathRes) is list:
            return cast(list[_Element], xpathRes)

        raise TypeError('XPath result is of the wrong type.')

    def get_div_descendants_by_type(
        self, 
        divtype: str, 
        lang: Optional[str]=None
    ) -> list[_Element]:

        """
        :param divtype: the value of the @type attribute of 
        the <div/>, e.g. "edition" or "translation"
        :param lang: the value of the @xml:lang attibute
        of the <div/> element. If None, treated as not specified.
        :return: a list of descendant elements where the
        @type attribute matches divtype.
        """

        try:
            if lang is None:
                return cast(
                    list[_Element], 
                    self.e.xpath(
                        f".//ns:div[@type='{divtype}']", 
                        namespaces={'ns': TEINS}) 
                    )
            
            elif lang is not None:
                return cast(list[_Element], self.e.xpath(
                    f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                    namespaces={'ns': TEINS, 'xml': XMLNS}) 
                )
            
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in getdivdescendants')
            print(e)
            return []
        
        except XMLSyntaxError as e:
            print('XMLSyntaxError in getdivdescendants')
            print(e)
            return []
        
        except AssertionError as e:
            print(e)
            return []
        
        return []

    def _load_e_from_file(self, inpt: Path | BytesIO) -> _Element:

        """
        Reads the root element from file and returns an
        _Element object representing the XML document
        """
        return self._load_etree_from_file(inpt=inpt).getroot()

    def _load_etree_from_file(self, inpt: Path | BytesIO) -> _ElementTree:
        """
        Reads the root element from file and returns an
        _ElementTree object representing the XML document
        """
        if not isinstance(inpt, (Path, BytesIO)):
            raise TypeError('filepath variable must be of type'
                            'Path')
        
        try:
            parser = etree.XMLParser(
                load_dtd=False,
                resolve_entities=False
            )
            self._roottree: _ElementTree = etree.parse(
                source=inpt, 
                parser=parser
            )

            return self._roottree
        
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in _e_from_file')
            print(e)
            return _ElementTree()
        
        except XMLSyntaxError as e:
            print('XMLSyntaxError in _e_from_file')
            handle_xmlsyntaxerror(e)
            return _ElementTree()        

    @property
    def processing_instructions(self) -> list[_ProcessingInstruction]:
        """
        Returns the processing instructions in the document.
        cf. https://lxml.de/api/lxml.etree._Element-class.html
        and https://stackoverflow.com/questions/57081539/access-the-processing-instructions-before-after-a-root-element-with-lxml,
        last accessed 03/08/2023
        """

        def _processing_instructions(
            acc:list[_ProcessingInstruction], 
            e:_Element | _ProcessingInstruction) -> list[_ProcessingInstruction]:

            previous = e.getprevious()

            if previous is None:
                return list(reversed(acc))
            
            if type(previous) is not _ProcessingInstruction:
                raise TypeError('_ProcessingInstruction expected.')
            
            return _processing_instructions(acc + [previous], previous)

        return _processing_instructions([], self.e)
    
    @property
    def processing_instructions_str(self) -> str:
        return '\n'.join([str(x) for x in self.processing_instructions])

    @property
    def root_elem(self) -> XmlElement:
        return XmlElement(self.e)

    @property
    def root_tree(self) -> _ElementTree:
        return self.e.getroottree()

    @property
    def text_desc(self) -> str:
        """
        Return the inner text of all the descendant nodes
        """
        if self.e is None: 
            return ''
        
        xpath_res = cast(list[str], self.e.xpath('.//text()'))

        return ''.join(xpath_res)

    def to_byte_str(self, collapse_empty_elements: bool = False) -> bytes:
        """
        Convert the XML to bytes including processing instructions
        """

        declaration = \
            '<?xml version="1.0" encoding="UTF-8"?>\n'.encode("utf-8")
        processing_instructions = \
            (self.processing_instructions_str + '\n').encode("utf-8")

        if collapse_empty_elements:
            self._collapse_empty_elements()

        try:
            b_str = etree.tostring( 
                self.e, 
                encoding='utf-8',   # type: ignore
                pretty_print=False,      # type: ignore
                xml_declaration=False   # type: ignore
            )
        except AssertionError as e:
            print(e)
            return b''

        return declaration + processing_instructions + b_str
    
    def to_str(self, collapse_empty_elements: bool = False) -> str:
        """
        Convert the XML to bytes including processing instructions
        """

        declaration = \
            '<?xml version="1.0" encoding="UTF-8"?>\n'
        processing_instructions = \
            (self.processing_instructions_str + '\n')

        if collapse_empty_elements:
            self._collapse_empty_elements()

        try:
            s = etree.tostring( 
                self.e, 
                pretty_print=False,      # type: ignore
                encoding='unicode',       # type: ignore
                xml_declaration=False   # type: ignore
            )
        except AssertionError as e:
            print(e)
            return ''

        return declaration + processing_instructions + s


    @property
    def valid(self) -> Optional[bool]:
        """
        :return: the result of the last validation attempt; None
        if no validation has been run
        """
        return self._valid

    @property
    def validation_result(self) -> str:
        """
        :return: a string giving the result of the last validation 
        attempt
        """
        if self.valid == True:
            return f'{self._p} is valid'
        elif self.valid == False:
            return f'{self._p} is not valid'
        else:
            return 'No validation has been carried out'

    def validate_by_isoschematron(self, fp: Path | str) -> bool:
        """
        Validates the EpiDoc file again a an ISOSchematron schema
        """

        fp_ = Path(fp)
        
        schematron_doc = etree.parse(fp_, parser=None)
        schematron = isoschematron.Schematron(schematron_doc)
        return schematron.validate(self.root_tree)

    def validate_by_relaxng(
            self, 
            relax_ng_path: Path | str) -> tuple[bool, str]:
        """
        Validates the EpiDoc file against a RelaxNG schema. 
        Runs the lxml xinclude method to include any modular elements, 
        see https://lxml.de/api.html#xinclude-and-elementinclude

        :return: a tuple containing a bool giving the validation result,
        as well as a message string.
        """

        relax_ng_path_ = Path(relax_ng_path)
        relax_ng_doc = etree.parse(source=relax_ng_path_, parser=None)
        relaxng = etree.RelaxNG(relax_ng_doc)
        
        try:
            roottree_ = deepcopy(self.root_tree)
            roottree_.xinclude()
            relaxng.assertValid(roottree_)
            msg = (f'{self._p} is valid EpiDoc according to the '
                    'RelaxNG schema')
            self._valid = True

        except DocumentInvalid:
            log = relaxng.error_log
            self._valid = False
            msg = log.last_error

        return (self._valid, msg)

    @property
    def xml_byte_str(self) -> bytes:
        """
        Return the element as a byte string
        """
        return self.to_byte_str(collapse_empty_elements=True)
    
    @property
    def xml_str(self) -> str:

        """
        Return the element as a unicode string
        """
        return self.to_str(collapse_empty_elements=True)
    
    def xpath(self, xpathstr: str) -> list[_Element | _ElementUnicodeResult]:
        if self.e is None: 
            return []
        try:
        # NB the cast won't necessarily be correct for all test cases
            return cast(
                list[Union[_Element,_ElementUnicodeResult]], 
                self.e.xpath(xpathstr, namespaces={'ns': TEINS})
            )
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in xpath')
            print(e)
            return []
        except XMLSyntaxError as e:
            print('XMLSyntaxError in xpath')
            handle_xmlsyntaxerror(e)
            return []