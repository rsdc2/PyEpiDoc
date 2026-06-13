from abc import abstractmethod
from .proiel_element import ProielElement
from .proiel_verse import ProielVerse
from .proiel_verse_token import ProielVerseToken
from .proiel_sentence import ProielSentence
from .proiel_token import ProielToken

class HasProielSentences(ProielElement):

    @property
    @abstractmethod
    def sentences(self) -> list[ProielSentence]:
        ...

    @property
    def sentence_tokens(self) -> list[ProielToken]:
        tokens = []
        for s in self.sentences:
            tokens.extend(s.tokens)
        return tokens
    
