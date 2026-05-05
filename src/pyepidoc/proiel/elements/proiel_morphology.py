
class ProielMorphology:

    _morph_str: str

    def __init__(self, morph_str: str):
        if len(morph_str) != 10:
            raise ValueError('Morphology string must be 10 characters long')
        self._morph_str = morph_str

    @property
    def _elements(self) -> list[str]:
        return list(self._morph_str)