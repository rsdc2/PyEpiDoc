from __future__ import annotations
from typing import (
    Optional, 
    Union, 
    cast, 
    overload, 
    Sequence
)
from pathlib import Path

from lxml import etree 
from lxml.etree import ( 
    _Comment,
    _Element, 
    _ElementTree, 
    _ElementUnicodeResult,
    _ProcessingInstruction,
    XMLSyntaxError,
    XMLSyntaxAssertionError
)

from ..constants import TEINS, XMLNS
from .baseelement import BaseElement
from .errors import handle_xmlsyntaxerror

class DocRoot:    
    _e: _Element
    _p: Path

    def __bytes__(self) -> bytes:
        """
        Convert the XML to bytes including processing instructions
        """

        declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'.encode("utf-8")
        processing_instructions = (self.processing_instructions_str + '\n').encode("utf-8")

        try:
            b_str = etree.tostring( 
                self.e, 
                pretty_print=True,      # type: ignore
                encoding='utf-8',       # type: ignore
                xml_declaration=False   # type: ignore
            )
        except AssertionError as e:
            print(e)
            return b''

        return declaration + processing_instructions + b_str

    @overload
    def __init__(self, inpt:Path):
        ...

    @overload
    def __init__(self, inpt:str):
        """
        :param inpt: str containing the filepath of the EpiDoc XML file.
        """
        ...

    @overload
    def __init__(self, inpt:_ElementTree):
        ...

    def __init__(self, inpt: Path | str | _ElementTree):
        if isinstance(inpt, Path):
            self._p = inpt
            if not inpt.exists():
                raise FileExistsError(f'File {inpt.absolute()} does not exist')
            self._e = self._e_from_file(inpt)
            return
        elif isinstance(inpt, _ElementTree):
            self._e = inpt.getroot()
            return
        elif isinstance(inpt, str):
            self._p = p = Path(inpt)
            if not p.exists():
                raise FileExistsError(f'File {p.absolute()} does not exist')
            self._e = self._e_from_file(p)
            return
        
        raise TypeError(f'input is of type {type(inpt)}, but should be either '
                        'Path, _ElementTree or str.')

    @staticmethod
    def _clean_text(text:str):
        return text.strip()\
            .replace('\n', '')\
            .replace(' ', '')\
            .replace('\t', '')

    @staticmethod
    def _compile_attribs(attribs: Optional[dict[str, str]]) -> str:
        if attribs is None:
            return ''
        return '[' + ''.join([f"@{k}='{attribs[k]}'" for k in attribs]) + ']'

    @property
    def depth(self) -> int:
        return 0

    @property
    def desc_comments(self) -> Sequence[BaseElement]:
        return [BaseElement(item) 
                for item in self._desc_comments]

    @property
    def _desc_comments(self) -> Sequence[_Comment]:
        if self.e is None:
            return []
        
        return [item for item in self.e.iterdescendants(tag=None)
                 if isinstance(item, _Comment)]

    @property
    def desc_elems(self) -> Sequence[BaseElement]:
        if self.e is None:
            return []
        
        return [BaseElement(item) 
                for item in self.e.iterdescendants(tag=None)
                 if isinstance(item, _Element)]

    def _e_from_file(self, filepath: Path) -> _Element:

        """
        Reads the root element from file and returns self._e
        """
        if not isinstance(filepath, Path):
            raise TypeError('filepath variable must be of type'
                            'Path')
        
        try:
            self._roottree:_ElementTree = etree.parse(
                source=filepath.absolute(), 
                parser=None # i.e. default
            )
            return self._roottree.getroot()
        
        except XMLSyntaxAssertionError as e:
            print('XMLSyntaxAssertionError in _e_from_file')
            print(e)
            return _Element()
        except XMLSyntaxError as e:
            print('XMLSyntaxError in _e_from_file')
            handle_xmlsyntaxerror(e)
            return _Element()

    @property
    def e(self) -> _Element:
        return self._e

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

        xpathstr = ' | '.join([f".//ns:{elemname}" + self._compile_attribs(attribs) for elemname in _elemnames])

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

    def get_div_descendants(
        self, 
        divtype:str, 
        lang:Optional[str]=None
    ) -> list[_Element]:

        if self.e is None: 
            return []

        if not lang:
            try:
                return cast(
                    list[_Element], 
                    self.e.xpath(
                        f".//ns:div[@type='{divtype}']", 
                        namespaces={'ns': TEINS}) 
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

        elif lang:
            return cast(list[_Element], self.e.xpath(
                f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': TEINS, 'xml': XMLNS}) 
            )
        
        return []

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
    def roottree(self) -> _ElementTree:
        return self.e.getroottree()

    @property
    def text_desc(self) -> str:
        if self.e is None: 
            return ''
        
        xpath_res = cast(list[str], self.e.xpath('.//text()'))

        return ''.join(xpath_res)

    def xpath(self, xpathstr:str) -> list[_Element | _ElementUnicodeResult]:
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