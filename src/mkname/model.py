"""
.. testsetup:: model

    from mkname.model import Name

.. _model:

##########
Data Model
##########

This will discuss the data model for :mod:`mkname` and related topics:

* :ref:`name_data`
* :ref:`model_api`


.. _name_data:

Name Data
=========
The core feature of :mod:`mkname` is the selection or generation of
names from a large list of names. The names used by :mod:`mkname`
are stored as :class:`mkname.model.Name` objects. These objects
store several pieces of information about its name in the following
fields:

*   :ref:`id`
*   :ref:`name`
*   :ref:`source`
*   :ref:`culture`
*   :ref:`date`
*   :ref:`gender`
*   :ref:`kind`

For example,For example, let's say you want to add the name "Graham," as in
the first name of "Graham Chapman" from Monty Python:

.. doctest:: model

    >>> name = Name(
    ...     id=0,
    ...     name='Graham',
    ...     source='https://montypython.com',
    ...     culture='MontyPython',
    ...     date=1941,
    ...     gender='python',
    ...     kind='given'
    ... )
    >>> name.name
    'Graham'


.. _name_fields:

Name Data Fields
----------------
The following are the data fields stored for a name in the names
database.


.. _id:

id
^^
This is a simple serial number used to uniquely identify the
:class:`mkname.model.Name` object when it is serialized in a
database or other output file.


.. _name:

name
^^^^
This is the name itself as a :class:`str` object.

The only limitation on this, beyond any set by the :class:`str` class,
is that it has a maximum size limit of 64 characters. This limit only
exists to provide a boundary for the database. Future versions of
:mod:`mkname` could increase it if there are cultures with names
longer than 64 characters.


.. _source:

source
^^^^^^
This is the source where the name was found as a :class:`str` object.

It's intended to be the specific URL for data the name was pulled from.
For example, some of the names in the default database were pulled from
the U.S. Census's list of most common surnames in 2010. The source field
for those names is the URL for that report on the U.S. Census website::

    https://www.census.gov/topics/population/genealogy/data/2010_surnames.html

There are three main reasons the source data is kept with the name:

*   It provides context for why the name is in the database.
*   It credits the people or organization that gathered the name data.
*   It allows data to be identified and pulled from the database if
    needed for some reason in the future.

The maximum length of a source is 128 characters.


.. _culture:

culture
^^^^^^^
This is the culture the name is from as a :class:`str` object.

As used in the default database, this is the nation associated with
the source I got the name from. However, this is intended to be
broader than that. It's, essentially, any grouping of people you
wish to associate the name to. For example, if you were adding
the names from the works of J. R. R. Tolkien, you may
mark the names of hobbits as "Hobbit" and those of dwarves as
"Dwarf." And, of course, you can split the elven names into "Sindar"
and "Quenyan," and so on.

The purpose of this field is to allow name generation to be narrowed
by culture. If you want to generate the name of someone from the
Roman Empire, you can limit name generation to just the "Roman"
culture.

The maximum length of a culture is 64 characters.


.. _date:

date
^^^^
The date associated with the data the name was taken from as an
:class:`int` object.

As used in the default database, this is the year for the name in
the Common Era (C.E.). Negative values are Before Common Era (B.C.E.).

The date is stored in the SQLite database as an `INTEGER`. This can be
up to an 8 byte, signed number, in case you are projecting names that
far into the future or the past.


.. _gender:

gender
^^^^^^
This is the "gender" of the name as a :class:`str` object.

Name data, especially "given" name data, tends to associate a
gender to a name. This gender is tracked in the gender field
for the record, so it can be used to filter the names used
when generating a name.

.. note:
    :mod:`mkname` wasn't built with the idea of surnames needing
    to match the gender of the given name, which creates a
    difficulty for names in cultures where that is needed, such
    as Russian. At time of writing, the "male" and "female"
    versions of Russian surnames are stored as separate names,
    so you'll need to filter the surnames by gender during
    generation to insure agreement between the gender of the
    given and surnames. Future versions may correct this, if
    it would be useful.

The maximum length of a gender is 64 characters.


.. _kind:

kind
^^^^
This is the position or function of the name as a :class:`str`
object.

As used in the default database, there are two kinds of names:

*   *given:* The name associated with the individual. In the United
    States this tends to be the name listed first, i.e. the "first
    name," but that's not true of all cultures.
*   *surname:* The name associated with a family. In the United
    States this tends to be the name listed last, i.e. the "last
    name," but that is not true for all cultures.

The maximum length of a kind is 16 characters.


.. _model_api:

Model API
=========
The following is a description of the public API for the data model.


.. _core_data:

Core Data
---------

.. autoclass:: mkname.model.Name


Validating Descriptors
----------------------
The following descriptors are used by :mod:`mkname.model.Name` to
validate and normalize data.

.. autoclass:: mkname.model.IsInt
.. autoclass:: mkname.model.IsStr

"""
from collections.abc import Callable, Sequence
from dataclasses import asdict, astuple, dataclass

from mkname.exceptions import StrExceedsUpperBound


# Types.
Section = dict[str, str]
Config = dict[str, Section]
SimpleMod = Callable[[str], str]
NameCensusRecord = tuple[str, ...]


# Descriptors.
class IsInt:
    """A data descriptor that ensures data is an :class:`int`.


    :param default: (Optional.) The default value, if any, of
        described attribute. Defaults to `0`.
    :returns: A :class:`mkname.model.IsInt` object.
    :rtype: mkname.model.IsInt
    """
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
    """A data descriptor that ensures data is an :class:`str`.

    :param default: (Optional.) The default value, if any, of
        described attribute. Defaults to an empty :class:`str`.
    :param size: (Optional.) The maximum length of the value
        of the described attribute. Defaults to 65,595.
    :returns: A :class:`mkname.model.IsStr` object.
    :rtype: mkname.model.IsStr
    """
    def __init__(self, *, default: str = '', size: int = 65_595) -> None:
        self._default = str(default)
        self.size = size

    def __set_name__(self, owner, name):
        self._name = '_' + name

    def __get__(self, obj, type) -> str:
        return getattr(obj, self._name)

    def __set__(self, obj, value) -> None:
        if len(value) > self.size:
            msg = f'String longer than {self.size} characters.'
            raise StrExceedsUpperBound(msg)
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

    :usage:

    .. doctest:: model

        >>> id = 1138
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
    name: IsStr = IsStr(size=64)
    source: IsStr = IsStr(size=128)
    culture: IsStr = IsStr(size=64)
    date: IsInt = IsInt()
    gender: IsStr = IsStr(size=64)
    kind: IsStr = IsStr(size=16)

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

    def asdict(self) -> dict[str, str | int]:
        """Serializes the object to a :class:`dict`."""
        return asdict(self)

    def astuple(self) -> tuple[int, str, str, str, int, str, str]:
        """Serializes the object to a :class:`tuple`."""
        return astuple(self)
