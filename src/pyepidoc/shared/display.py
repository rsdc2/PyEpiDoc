# Provides functions for showing elements
from typing import Iterable
from ..epidoc.dom import doc_id, lang
from ..epidoc.epidoc_element import EpiDocElement


def show_items(
    items: Iterable, 
    sep: str='\n', 
    prefix: str='- '
) -> str:
    
    """
    :param prefix: string to place before each item; defaults to '- '
    :param sep: string to place after each item; defaults to new line
    :return: a string representation of all the items in a list
    """
    return sep.join([f'{prefix}{str(item)}' 
                           for item in items])


def print_items(
    items: Iterable,
    sep: str='\n',
    prefix: str='- '
) -> None:
    """
    Output a list to stdout
    """

    print(show_items(items, sep, prefix))


def show_elems(
    elems: Iterable[EpiDocElement],
    sep: str='\n', 
    prefix: str='- ',
    include_source_doc_ids: bool=True,
    include_langs: bool=True
) -> str:

    """
    Returns a string with the string representation 
    of each element printed separated by "sep".
    If "include_source_doc_ids" is True, prints the document source id.
    If "include_langs" is True, includes the language of the instance.
    """
    
    if include_source_doc_ids and not include_langs:
        sources = [doc_id(elem) for elem in elems]
        return sep.join(f'{prefix}{source}: {elem}' for elem, source in zip(elems, sources))

    if include_source_doc_ids and include_langs:
        sources = [doc_id(elem) for elem in elems]
        langs = [lang(elem) for elem in elems]
        return sep.join(f'{prefix}{source}: {elem} ({lang})' 
            for elem, source, lang in zip(elems, sources, langs))

    return sep + sep.join([f'{prefix}{str(elem)}' for elem in elems])

