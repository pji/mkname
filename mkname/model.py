"""
model
~~~~~

The data model for the mkname package.
"""
from typing import NamedTuple


class Name(NamedTuple):
    id: int
    name: str
    source: str
    culture: str
    data: int
    gender: str
    kind: str
