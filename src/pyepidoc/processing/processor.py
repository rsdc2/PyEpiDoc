from __future__ import annotations
from typing import Callable, Literal

from pyepidoc import EpiDoc
from pyepidoc.epidoc.metadata.resp_stmt import RespStmt
from pyepidoc.epidoc.metadata.change import Change

from .operations import apply_lemmatization


class Processor:
    """
    Contains methods for processing EpiDoc files, e.g.
    tokenization, lemmatization, setting IDs
    """

    _epidoc: EpiDoc

    def __init__(self, epidoc: EpiDoc):
        self._epidoc = epidoc

    @property
    def epidoc(self) -> EpiDoc:
        return self._epidoc
    
    def lemmatize(
            self, 
            lemmatize: Callable[[str], str],
            where: Literal['main', 'separate'],
            resp_stmt: RespStmt | None = None,
            change: Change | None = None,
            verbose = False
        ) -> Processor:

        """
        Lemmatize the EpiDoc file according to the `lemmatize`
        callback
        """

        lemmatized = apply_lemmatization(
            self.epidoc,
            lemmatize,
            where,
            resp_stmt,
            change, 
            verbose
        )

        return Processor(lemmatized)
    
    # def sync_lemmatized_edition(self) -> Processor:
        
    #     """
    #     Ensure the simple-lemmatized edition matches the main
    #     edition
    #     """

