from pyepidoc import EpiDoc

class Processor:
    """
    Parent class for all processor classes, e.g. Tokenizer and Lemmatizer
    """

    _epidoc: EpiDoc

    def __init__(self, epidoc: EpiDoc):
        self._epidoc = epidoc

    @property
    def epidoc(self) -> EpiDoc:
        return self._epidoc