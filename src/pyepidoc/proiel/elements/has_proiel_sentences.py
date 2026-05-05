from abc import abstractmethod
from .proiel_element import ProielElement
from .proiel_token import ProielToken
from .proiel_sentence import ProielSentence

class HasProielSentences(ProielElement):

    @property
    @abstractmethod
    def sentences(self) -> list[ProielSentence]:
        ...

    @property
    def tokens(self) -> list[ProielToken]:
        tokens = []
        for s in self.sentences:
            tokens.extend(s.tokens)
        return tokens