from .proiel_element import ProielElement
from .proiel_verse_token import ProielToken


class ProielSentence(ProielElement):
    
    @property
    def tokens(self) -> list[ProielToken]:
        token_elements = self._e.child_elements_by_local_name('token')
        tokens = [ProielToken(token) for token in token_elements if token.get_attr('form') is not None]
        return tokens