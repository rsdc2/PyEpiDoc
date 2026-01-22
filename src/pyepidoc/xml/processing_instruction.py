from lxml.etree import _ProcessingInstruction

class ProcessingInstruction:
    _processing_instruction: _ProcessingInstruction

    def __init__(self, processing_instruction: _ProcessingInstruction):
        self._processing_instruction = processing_instruction

    @property
    def localname(self) -> str:
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        raise NotImplementedError()