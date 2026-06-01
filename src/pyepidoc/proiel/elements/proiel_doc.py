from pathlib import Path
from pyepidoc.xml import XmlElement
from pyepidoc.xml import XmlRoot
from pyepidoc.shared.bible_refs.bible_book import BibleBook

from .has_proiel_sentences import HasProielSentences
from .proiel_source import ProielSource
from .proiel_div import ProielDiv
from .proiel_sentence import ProielSentence
from .proiel_bible_ref import ProielBibleRef
from .proiel_chapter import ProielChapter
from .proiel_verse import ProielVerse
from .proiel_token import ProielToken

class ProielDoc(HasProielSentences):
    _root: XmlRoot

    def __init__(
            self, 
            inpt: Path | str | XmlElement | XmlRoot):

        if isinstance(inpt, Path):
            self._root = XmlRoot(inpt)
            self._e = self._root._e

        elif isinstance(inpt, str):
            self._root = XmlRoot(inpt)
            self._e = self._root._e

        elif isinstance(inpt, XmlElement):
            self._e = inpt
            self._root = XmlRoot(self._e.roottree)

        elif isinstance(inpt, XmlRoot):
            self._root = inpt
            self._e = self._root._e

        else:
            raise TypeError(f'Cannot create ProielDoc from {type(inpt)}')

    @property
    def source(self) -> ProielSource:
        source = self._e.child_element_by_local_name('source')
        if source is None:
            raise ValueError('Source cannot be None')
        
        return ProielSource(source)
    
    @property
    def divs(self) -> list[ProielDiv]:
        return self.source.divs
    
    @property
    def sentences(self) -> list[ProielSentence]:
        return self.source.sentences
    
    def chapter(self, book: str, chapter: int) -> ProielChapter | None:
        for div in self.divs:
            first_token_citation = div.tokens[0].citation
            if first_token_citation.book == BibleBook(book) and \
                first_token_citation.chapter == chapter:

                return ProielChapter(div._e)
            
        return None
        
        


                

