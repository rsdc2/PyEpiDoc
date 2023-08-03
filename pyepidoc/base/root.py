from __future__ import annotations
from typing import Optional, Union, cast

from lxml import etree # type: ignore
from lxml.etree import ( # type: ignore
    _Element as _Element, 
    _ElementTree, 
    _ElementUnicodeResult,
    XMLSyntaxError
)

from ..file import FileInfo
from ..constants import NS, XMLNS


class DocRoot:    
    _e: Optional[_Element]
    _file: Optional[FileInfo]
    _roottree: Optional[_ElementTree]

    def __init__(self, input:FileInfo | _ElementTree | str, fullpath=False):
        if type(input) is FileInfo:
            self._file = input
            self._e = None
            return
        elif type(input) is _ElementTree:
            self._e = input.getroot()
            self._roottree = input
            self._file = None
            return
        elif type(input) is str:
            self._file = FileInfo(
                filepath=input, 
                fullpath=fullpath,
            )
            self._e = None
            return
        
        raise TypeError(f"input is of type {type(input)}, but should be either FileInfo, _ElementTree or str.")

    @staticmethod
    def _clean_text(text:str):
        return text.strip()\
            .replace('\n', '')\
            .replace(' ', '')\
            .replace('\t', '')

    @staticmethod
    def _compile_attribs(attribs:Optional[dict[str, str]]) -> str:
        if attribs is None:
            return ''
        return '[' + ''.join([f"@{k}='{attribs[k]}'" for k in attribs]) + ']'

    @property
    def depth(self) -> int:
        return 0

    @property
    def e(self) -> Optional[_Element]:
        if self._e is None:
            if self._file is None: 
                raise TypeError("self._file is None")

            try:
                self._roottree = etree.parse(self._file.full_filepath)
                self._e = self._roottree.getroot()

                return self._e
            except XMLSyntaxError:
                print(f'XML syntax error in {self._file.filename}')
                return _Element()
        
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

        xpathRes = (self
            .e
            .xpath(xpathstr, namespaces={'ns': NS})
        )

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
            return cast(list[_Element], self.e.xpath(f".//ns:div[@type='{divtype}']", namespaces={'ns': NS}) )

        elif lang:
            return cast(list[_Element], self.e.xpath(
                f".//ns:div[@type='{divtype} @xml:lang='{lang}']",
                namespaces={'ns': NS, 'xml': XMLNS}) 
            )
        
        return []

    @property
    def headers(self):
        pass

    @property
    def text_desc(self) -> str:
        if self.e is None: 
            return ''
        
        xpath_res = cast(list[str], self.e.xpath('.//text()'))

        return ''.join(xpath_res)

    def xpath(self, xpathstr:str) -> list[_Element | _ElementUnicodeResult]:
        if self.e is None: 
            return []

        # NB the cast won't necessarily be correct for all test cases
        return cast(list[Union[_Element,_ElementUnicodeResult]], self.e.xpath(xpathstr, namespaces={'ns': NS}))