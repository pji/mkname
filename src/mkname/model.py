"""
model
~~~~~

The data model for :mod:`mkname`.

.. autoclass:: mkname.model.Name

"""
from typing import NamedTuple


class Name(NamedTuple):
    """A name to use for generation.

    :param id: A unique identifier for the name.
    :param name: The name.
    :param source: The URL where the name was found.
    :param culture: The culture or nation the name is tied to.
    :param date: The approximate year the name is tied to.
    :param gender: The gender typically associated with the name
        during the time and in the culture the name is from.
    :param kind: A tag for how the name is used, such as a given
        name or a surname.

    Usage::

        >>> id = 1138                       # doctest: +ELLIPSIS
        >>> name = 'Graham'
        >>> src = 'Monty Python'
        >>> culture = 'UK'
        >>> date = 1941
        >>> gender = 'python'
        >>> kind = 'given'
        >>> Name(id, name, src, culture, date, gender, kind)
        Name(id=1138, name='Graham', source='Monty Python'...
    """
    id: int
    name: str
    source: str
    culture: str
    date: int
    gender: str
    kind: str
