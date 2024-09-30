from __future__ import annotations
from typing import TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')


def dict_remove_none(d: dict[T, U | None]) -> dict[T, U]:
    return {
        k: v for k, v in d.items()
        if v is not None
    }