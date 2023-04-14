# Provides functions for showing elements
from typing import Sequence
from .epidoc.funcs import doc_id
from .base import Element

def show_elems(
    elems:Sequence[Element],
    sep:str='\n', 
    prefix:str='- ',
    source_docs:bool=True
) -> str:

    """
    Returns a string with the string representation 
    of each element printed separated by "sep".
    If "source_docs" is True, prints the document 
    source.
    """

    if source_docs:
        sources = [doc_id(elem) for elem in elems]
        return sep.join(f'{prefix}{source}: {elem}' for elem, source in zip(elems, sources))

    return sep + sep.join([f'{prefix}{str(elem)}' for elem in elems])

