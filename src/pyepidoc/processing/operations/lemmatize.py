from typing import Callable, Literal

from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.resp_stmt import RespStmt
from pyepidoc.epidoc.metadata.change import Change
from pyepidoc.epidoc import enums

def apply_lemmatization(
        epidoc: EpiDoc, 
        lemmatize: Callable[[str], str],
        where: Literal['main', 'separate'],
        resp_stmt: RespStmt | None = None,
        change: Change | None = None,
        verbose = False
    ) -> EpiDoc:

    """
    Lemmatize all the <w> elements in 
    the EpiDoc document.

    :param lemmatize: a function with one parameter,
    the form needing lemmatization, returning the 
    lemma.

    :param where: where to put the lemmatized version,
    either on a separate <div> or on the main <div>. 
    If a separate edition is not present, one is created 
    containing copies of the elements that need lemmatizing.
    """

    main_edition = epidoc.edition_by_subtype(None)
    if main_edition is None:
        raise ValueError('No main edition could be found.')

    if where == 'separate':
        # Create a separate lemmatized edition if not already present
        lemmatized_edition = epidoc.edition_by_subtype('simple-lemmatized') 

        if lemmatized_edition is None:
            lemmatized_edition = epidoc._append_new_lemmatized_edition(resp=resp_stmt)
            epidoc.body.copy_edition_items_to_appear_in_lemmatized_edition(
                source=main_edition, 
                target=lemmatized_edition
            )

        edition = lemmatized_edition

    elif where == 'main':
        edition = main_edition
    else:
        raise TypeError(
            f'Invalid destination for lemmatized items: {where}')

    for w in edition.w_tokens:
        w.lemma = lemmatize(w.normalized_form or '')
    
    if resp_stmt:
        epidoc._append_resp_stmt(resp_stmt)

    if change:
        epidoc._append_change(change)

    epidoc.prettify(prettifier='pyepidoc', verbose=verbose)
    
    return epidoc


def sync_lemmatized_edition(epidoc: EpiDoc):
    """
    Ensure the `simple-lemmatized` edition matches the main
    edition
    """
    if epidoc.main_edition is None:
        raise ValueError('No main edition present. Cannot sync lemmatized edition')

    lemmatizable_elements = [
        elem for elem in epidoc.main_edition.representable_no_subatomic
        if elem.localname in enums.StandoffEditionElements
    ]

    lemmatized_elements = epidoc.simple_lemmatized_edition





