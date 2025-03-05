"""
model
~~~~~

The data model for :mod:`mkname`.

.. autoclass:: mkname.model.Name

"""
from collections.abc import Callable, Sequence
from dataclasses import astuple, dataclass


# Types.
Section = dict[str, str]
Config = dict[str, Section]
SimpleMod = Callable[[str], str]
NameCensusRecord = tuple[str, ...]


# Descriptors.
class IsInt:
    """A data descriptor that ensures data is an :class:`int`."""
    def __init__(self, *, default: int = 0) -> None:
        self._default = int(default)

    def __set_name__(self, owner, name):
        self._name = '_' + name

    def __get__(self, obj, type) -> int:
        return getattr(obj, self._name)

    def __set__(self, obj, value) -> None:
        try:
            normal = int(value)
        except ValueError:
            normal = 0
        setattr(obj, self._name, normal)


class IsStr:
    """A data descriptor that ensures data is an :class:`str`."""
    def __init__(self, *, default: str = '') -> None:
        self._default = str(default)

    def __set_name__(self, owner, name):
        self._name = '_' + name

    def __get__(self, obj, type) -> str:
        return getattr(obj, self._name)

    def __set__(self, obj, value) -> None:
        setattr(obj, self._name, str(value))


# Dataclasses.
@dataclass
class Name:
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
    id: IsInt = IsInt()
    name: IsStr = IsStr()
    source: IsStr = IsStr()
    culture: IsStr = IsStr()
    date: IsInt = IsInt()
    gender: IsStr = IsStr()
    kind: IsStr = IsStr()

    @classmethod
    def from_name_census(
        cls, data: NameCensusRecord,
        source: str,
        date: int,
        kind: str,
        id_: int = 0
    ) -> 'Name':
        """Deserialize data in census.name format.

        :param data: The census.name data to deserialize. It will
            detect whether the type is for given or surnames based
            on the length of the record.
        :param source: The URL for the data source.
        :param date: The year the data comes from.
        :param kind: A tag for how the name is used, such as a given
            name or a surname.
        :param id_: The unique ID for the name.
        :returns: A :class:`mkname.model.Name` object.
        :rtype: mkname.model.Name
        """
        name_index = 0
        culture_index = 3
        unisex_index = 7
        gender_index = 6

        is_given = True if len(data) == 10 else False
        unisex_val = True if data[unisex_index].casefold() == 'y' else False
        gender_val = data[gender_index].casefold()
        if is_given and not unisex_val and gender_val == 'm':
            gender = 'male'
        elif is_given and not unisex_val and gender_val == 'f':
            gender = 'female'
        elif is_given and unisex_val:
            gender = 'none'
        elif not is_given and gender_val == 'm':
            gender = 'male'
        elif not is_given and gender_val == 'f':
            gender = 'female'
        elif not is_given and not gender_val:
            gender = 'none'
        else:
            gender = gender_val

        return cls(
            id=id_,
            name=data[name_index],
            source=source,
            culture=data[culture_index],
            date=date,
            gender=gender,
            kind=kind
        )

    def astuple(self) -> tuple[int, str, str, str, int, str, str]:
        """Serializes the object to a :class:`tuple`."""
        return astuple(self)
