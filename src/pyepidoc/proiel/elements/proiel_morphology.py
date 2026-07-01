
class ProielMorphology:

    _morph_str: str

    def __init__(self, morph_str: str):
        if len(morph_str) != 10:
            raise ValueError('Morphology string must be 10 characters long')
        self._morph_str = morph_str

    @property
    def _elements(self) -> list[str]:
        return list(self._morph_str)
    
    @property
    def mood(self) -> str:
        return self._elements[3].lower()
    
    @property
    def morph_str(self) -> str:
        return self.morph_str.lower()

    @property
    def tense(self) -> str:
        return self._elements[2].lower()

    @property
    def voice(self) -> str:
        return self._elements[4].lower()