from __future__  import annotations
from lxml.etree import _ProcessingInstruction

class ProcessingInstruction:
    _e: _ProcessingInstruction

    def __init__(self, processing_instruction: _ProcessingInstruction):
        self._e = processing_instruction

    @property
    def localname(self) -> str:
        raise NotImplementedError()
    
    @property
    def previous_sibling(self) -> ProcessingInstruction | None:
        """
        Return the previous sibling node.
        """
        _prev = self._e.getprevious()
        if isinstance(_prev, _ProcessingInstruction):
            return ProcessingInstruction(_prev)
        if _prev is None:
            return None

        raise TypeError(f"Previous element is of type {type(_prev)}.")

    @property
    def text(self) -> str:
        raise NotImplementedError()
