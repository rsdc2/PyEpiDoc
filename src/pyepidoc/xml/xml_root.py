from __future__ import annotations
from typing import (
    Optional, 
    cast, 
    overload
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

from pyepidoc.xml.xml_element import XmlElement
from .xml_element import XmlElement, XmlNode, XmlText
from .processing_instruction import ProcessingInstruction
from .errors import handle_xmlsyntaxerror

class XmlRoot:  
    _tree: _ElementTree
    _path: Path
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
            self._path = inpt
            if not inpt.exists():
                raise FileExistsError(f'File {inpt.absolute()} does not exist')
            self._tree = self._load_etree_from_file(inpt)
            return
        
        elif isinstance(inpt, BytesIO):
            self._tree = self._load_etree_from_file(inpt)
            return
            
        elif isinstance(inpt, _ElementTree):
            self._tree = inpt
            return

        elif isinstance(inpt, _Element):
            self._tree = inpt.getroottree()
            return

        elif isinstance(inpt, XmlElement):
            self._tree = inpt.roottree
            return
        
        elif isinstance(inpt, str):
            self._path = path = Path(inpt)
            if not path.exists():
                raise FileExistsError(f'File {path.absolute()} does not exist')
            self._tree = self._load_etree_from_file(path)
            return
        
        raise TypeError(f'input is of type {type(inpt)}, but should be either '
                        'Path, _ElementTree, _Element, BaseElement or str.')

    @staticmethod
    def _clean_text(text:str):
        return text.strip()\
            .replace('\n', '')\
            .replace(' ', '')\
            .replace('\t', '')

    def _collapse_empty_elements(self) -> XmlRoot:
        """
        Turn a <tag></tag> to <tag/>
        """

        for elem in self.root.descendant_elements:
            if elem.text == '':
                elem.text = None 

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
    def filename(self) -> str:
        return self._path.stem

    @staticmethod
    def _load_etree_from_file(inpt: Path | BytesIO) -> _ElementTree:
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
            tree = etree.parse(
                source=inpt, 
                parser=parser
            )
            return tree
        
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in _e_from_file')
            print(e)
            return XmlRoot(_ElementTree())
        
        except XMLSyntaxError as e:
            print('XMLSyntaxError in _e_from_file')
            print(e)
            return _ElementTree()        
        
    def _prettify_with_lxml(self) -> XmlRoot:

        """
        Use the prettifier in `lxml` to prettify the 
        xml file. Deepcopies the file.
        """
        
        prettified_str: bytes = self.root.to_bytes(
            xml_declaration=True, 
            pretty_print=True)
        
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
        prettified_doc = XmlRoot(tree)

        return prettified_doc
    
    @property
    def processing_instructions(self) -> list[ProcessingInstruction]:
        """
        Returns the processing instructions in the document.
        cf. https://lxml.de/api/lxml.etree._Element-class.html
        and https://stackoverflow.com/questions/57081539/access-the-processing-instructions-before-after-a-root-element-with-lxml,
        last accessed 03/08/2023
        """

        def _processing_instructions(
            acc: list[ProcessingInstruction], 
            e: XmlElement | ProcessingInstruction) -> list[ProcessingInstruction]:

            previous = e.previous_sibling

            if previous is None:
                return list(reversed(acc))
            
            if not isinstance(previous, ProcessingInstruction):
                raise TypeError('ProcessingInstruction expected.')
            
            return _processing_instructions(acc + [previous], previous)

        return _processing_instructions([], self.root)
    
    @property
    def processing_instructions_str(self) -> str:
        return '\n'.join([str(x) for x in self.processing_instructions])
    
    @property
    def root(self) -> XmlElement:
        return XmlElement(self._tree.getroot())

    @property
    def root_tree(self) -> _ElementTree:
        return self.root._e.getroottree

    @property
    def text_desc(self) -> str:
        """
        Return the inner text of all the descendant nodes
        """
        
        xpath_result: list[XmlText] = cast(list[XmlText], self.root.xpath('.//text()'))
        return ''.join([text.text for text in xpath_result])

    def to_bytes(self, collapse_empty_elements: bool = False) -> bytes:
        """
        Convert the XML to bytes including processing instructions
        """

        declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'.encode("utf-8")
        processing_instructions = \
            (self.processing_instructions_str + '\n').encode("utf-8")

        if collapse_empty_elements:
            self._collapse_empty_elements()

        try:
            b_str = etree.tostring( 
                self.root._e, 
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
                self.root._e, 
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
            return f'{self._path} is valid'
        elif self.valid == False:
            return f'{self._path} is not valid'
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
            msg = (f'{self._path} is valid EpiDoc according to the '
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
        return self.to_bytes(collapse_empty_elements=True)

    @property
    def xml_str(self) -> str:

        """
        Return the element as a unicode string
        """
        return self.to_str(collapse_empty_elements=True)
    
    def xpath(self, xpathstr: str) -> list[XmlNode]:
        return self.root.xpath(xpathstr)