from typing import Callable, Literal

from pyepidoc import EpiDoc
from pyepidoc.epidoc.edition_elements.edition import Edition
from pyepidoc.epidoc.metadata.resp_stmt import RespStmt
from pyepidoc.epidoc.metadata.change import Change
from pyepidoc.epidoc import enums
from pyepidoc.shared.generic_collection import GenericCollection as Collection, remove_none
from pyepidoc.epidoc.representable import Representable

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
            lemmatized_edition = epidoc.ensure_lemmatized_edition(resp=resp_stmt)
            epidoc.body.copy_lemmatizable_to_lemmatized_edition(
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
        epidoc.append_resp_stmt(resp_stmt)

    if change:
        epidoc.append_change(change)

    epidoc.prettify(prettifier='pyepidoc', verbose=verbose)
    
    return epidoc


def update_lemmatized_edition(
        epidoc: EpiDoc, 
        lemmatize: Callable[[str], str], 
        change: Change | None = None) -> EpiDoc:
    """
    Ensure the `simple-lemmatized` edition matches the main
    edition
    """
    # Validate
    if epidoc.main_edition is None:
        raise ValueError('No main edition present. '
                         'Cannot update lemmatized edition')
    if epidoc.simple_lemmatized_edition is None:
        raise ValueError('No lemmatized edition present. '
                         'Cannot update lemmatized edition')

    # Arrange
    old_lemmatized_edition = Edition(epidoc.simple_lemmatized_edition.deepcopy())
    old_lemmatized_edition_ids = old_lemmatized_edition.local_ids
    epidoc.simple_lemmatized_edition.remove_children()
    new_lemmatized_edition = epidoc.body.copy_lemmatizable_to_lemmatized_edition(
        epidoc.main_edition, 
        epidoc.simple_lemmatized_edition
    )

    # Act
    for w in new_lemmatized_edition.w_tokens:
        if w.local_id and w.local_id in old_lemmatized_edition_ids:
            old_token = old_lemmatized_edition.token_by_local_id(w.local_id)
            if old_token is None:
                raise TypeError('No token with local id (@n attribute) '
                                f'{w.local_id} in lemmatized edition')
            w.lemma = old_token.lemma
                
        else:
            w.lemma = lemmatize(w.normalized_form or '')

    epidoc.prettify()
    if change and old_lemmatized_edition_ids != new_lemmatized_edition.local_ids:
        epidoc.append_change(change)
    return epidoc
            
    




