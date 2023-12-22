"""
Functions for providing instances of abbreviation distributions in 
an EpiDoc corpus
"""
from typing import Iterable
from pyepidoc import EpiDocCorpus
from pyepidoc.epidoc.expan import Expan
from pyepidoc.shared_types import SetRelation
from pyepidoc.epidoc.funcs import lang