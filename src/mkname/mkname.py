"""
.. _name_gen:

Name Generation and Selection
=============================
These functions generate names using the data in the
:ref:`names database <names_db>`. They handle gathering
the :ref:`name data <name_data>`, reading the
:ref:`configuration <config>`, generating the name,
and `simple modification <simple_mod>`.

.. autofunction:: mkname.create_compound_name
.. autofunction:: mkname.create_syllable_name
.. autofunction:: mkname.pick_name


Manually Configured Generation and Selection
--------------------------------------------
The following functions can also generate names, but they require
a little more work on your part to manage the configuration. Only
use these if, for some reason, you need to get between the process
of loading the configuration or names from the names database and
the generation of the name:

.. autofunction:: mkname.build_compound_name
.. autofunction:: mkname.build_from_syllables
.. autofunction:: mkname.select_name


Name Listing
============
The following function will list the names in the current
names database.

.. autofunction:: mkname.list_names

"""
from collections.abc import Sequence
from pathlib import Path
from warnings import warn

from mkname.constants import *
from mkname.db import get_names
from mkname.init import get_config, get_db
from mkname.mod import compound_names, mods
from mkname.model import Name, Section, SimpleMod
from mkname.utility import roll, split_into_syllables


# Names that will be imported when using *.


__all__ = [
    'build_compound_name',
    'build_compound_name_from_names',
    'build_from_syllables',
    'build_syllable_name_from_names',
    'configure',
    'create_compound_name',
    'create_syllable_name',
    'list_names',
    'pick_name',
    'select_name',
    'select_name_from_names'
]


# Complete functions for making names.
def create_compound_name(
    num_names: int = 1,
    mod: SimpleMod | None = None,
    source: str | None = None,
    culture: str | None = None,
    date: int | None = None,
    gender: str | None = None,
    kind: str | None = None,
    cfg_path: Path | str | None = None,
    db_path: Path | str | None = None
) -> list[str]:
    """Generate a name by combining two random names.

    :param num_names: (Optional.) The number of names
        to create. Defaults to one.
    :param mod: (Optional.) A simple modification
        function for modifying the created names.
        Defaults to not modifying the names.
    :param source: (Optional.) Limit the names
        used to the given :ref:`source<source>`
        Defaults to all sources.
    :param culture: (Optional.) Limit the names
        used to the given :ref:`culture<culture>`
        Defaults to all cultures.
    :param date: (Optional.) Limit the names
        used to the given :ref:`date<date>`
        Defaults to all dates.
    :param gender: (Optional.) Limit the names
        used to the given :ref:`gender<gender>`
        Defaults to all genders.
    :param kind: (Optional.) Limit the names
        used to the given :ref:`kind<kind>`
        Defaults to all kinds.
    :param cfg_path: (Optional.) The path to a
        :ref:`configuration file<config>`.
        Defaults to searching for config files.
    :param db_path: (Optional.) The path to a
        :ref:`names database<names_db>`.
        Defaults to :ref:`searching<db_search>`
        for the database.
    :returns: A :class:`list` object.
    :rtype: list

    :usage:

    To generate a compound name:

    .. testsetup:: create_compound_name

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import create_compound_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: create_compound_name

        >>> create_compound_name()
        ['Sethel']

    To generate three compound names:

    .. doctest:: create_compound_name

        >>> create_compound_name(3)
        ['Herika', 'Betty', 'Warthur']

    To force :func:`mkname.create_compound_name` to use
    a custom names database you built. It will also use
    this database if it's the first found during a search,
    but this will override that search:

    .. doctest:: create_compound_name

        >>> create_compound_name(db_path='tests/data/names.db')
        ['Tam']

    To force :func:`mkname.create_compound_name` to use
    a custom configuration you built. It will also use
    this configuration if it's the last found during
    a search, but this will override that search. This
    can be used to change how :func:`mkname.create_compound_name`
    combines the names:

    .. testsetup:: create_compound_name_cfg

        from mkname import create_compound_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: create_compound_name_cfg

        >>> create_compound_name(cfg_path='tests/data/test_config_full.toml')
        ['Haffles']

    To generate a name from only male given names:

    .. doctest:: create_compound_name

        >>> create_compound_name(gender='male', kind='given')
        ['Llike']

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [build_compound_name_from_names(
        names,
        config['consonants'],
        config['vowels']
    ) for _ in range(num_names)]
    results = modify(results, mod)
    return results


def create_syllable_name(
    num_syllables: int,
    num_names: int = 1,
    mod: SimpleMod | None = None,
    source: str | None = None,
    culture: str | None = None,
    date: int | None = None,
    gender: str | None = None,
    kind: str | None = None,
    cfg_path: Path | str | None = None,
    db_path: Path | str | None = None
) -> list[str]:
    """Generate a name by combining syllables from random names.

    :param num_syllables: The number of syllables
        in the creeated names.
    :param num_names: (Optional.) The number of names
        to create. Defaults to one.
    :param mod: (Optional.) A simple modification
        function for modifying the created names.
        Defaults to no modifying the names.
    :param source: (Optional.) Limit the names
        used to the given :ref:`source<source>`
        Defaults to all sources.
    :param culture: (Optional.) Limit the names
        used to the given :ref:`culture<culture>`
        Defaults to all cultures.
    :param date: (Optional.) Limit the names
        used to the given :ref:`date<date>`
        Defaults to all dates.
    :param gender: (Optional.) Limit the names
        used to the given :ref:`gender<gender>`
        Defaults to all genders.
    :param kind: (Optional.) Limit the names
        used to the given :ref:`kind<kind>`
        Defaults to all kinds.
    :param cfg_path: (Optional.) The path to a
        :ref:`configuration file<config>`.
        Defaults to searching for config files.
    :param db_path: (Optional.) The path to a
        :ref:`names database<names_db>`.
        Defaults to :ref:`searching<db_search>`
        for the database.
    :returns: A :class:`list` object.
    :rtype: list

    :usage:

    To generate a three syllable name:

    .. testsetup:: create_syllable_name

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import create_syllable_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: create_syllable_name

        >>> create_syllable_name(3)
        ['Yerethar']

    To generate three compound names:

    .. doctest:: create_syllable_name

        >>> create_syllable_name(3, num_names=3)
        ['Wilhurgar', 'Bassjuane', 'Bertollan']

    To force :func:`mkname.create_syllable_name` to use
    a custom names database you built. It will also use
    this database if it's the first found during a search,
    but this will override that search:

    .. doctest:: create_syllable_name

        >>> create_syllable_name(3, db_path='tests/data/names.db')
        ['Spamlesham']

    To force :func:`mkname.create_syllable_name` to use
    a custom configuration you built. It will also use
    this configuration if it's the last found during
    a search, but this will override that search. This
    can be used to change how :func:`mkname.create_compound_name`
    combines the names:

    .. doctest:: create_syllable_name

        >>> path = 'tests/data/test_config_full.toml'
        >>> create_syllable_name(3, cfg_path=path)
        ['Spamhamspam']

    To generate a four syllable name from only male given names:

    .. doctest:: create_syllable_name

        >>> create_syllable_name(4, gender='male', kind='given')
        ['Hontinryal']

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [build_syllable_name_from_names(
        num_syllables,
        names,
        config['consonants'],
        config['vowels']
    ) for _ in range(num_names)]
    results = modify(results, mod)
    return results


def list_names(
    source: str | None = None,
    culture: str | None = None,
    date: int | None = None,
    gender: str | None = None,
    kind: str | None = None,
    cfg_path: Path | str | None = None,
    db_path: Path | str | None = None
) -> list[str]:
    """List names in the :ref:`names database<names_db>`.

    :param num_names: (Optional.) The number of names
    :param source: (Optional.) Limit the names
        used to the given :ref:`source<source>`
        Defaults to all sources.
    :param culture: (Optional.) Limit the names
        used to the given :ref:`culture<culture>`
        Defaults to all cultures.
    :param date: (Optional.) Limit the names
        used to the given :ref:`date<date>`
        Defaults to all dates.
    :param gender: (Optional.) Limit the names
        used to the given :ref:`gender<gender>`
        Defaults to all genders.
    :param kind: (Optional.) Limit the names
        used to the given :ref:`kind<kind>`
        Defaults to all kinds.
    :param cfg_path: (Optional.) The path to a
        :ref:`configuration file<config>`.
        Defaults to searching for config files.
    :param db_path: (Optional.) The path to a
        :ref:`names database<names_db>`.
        Defaults to :ref:`searching<db_search>`
        for the database.
    :returns: A :class:`list` object.
    :rtype: list

    :usage:

    To list all the names in the default names database:

    .. doctest:: api

        >>> list_names()
        ['Noah', 'Liam', 'Jacob', 'Will...

    To list all the names in a custom names database. You can also
    list the names in a custom database if it is the first found
    during the :ref:`database search<db_search>`, but this will
    override that search:

    .. doctest:: api

        >>> list_names(db_path='tests/data/names.db')
        ['spam', 'ham', 'tomato'...

    To force :func:`mkname.list_names` to use
    a custom configuration you built. It will also use
    this configuration if it's the last found during
    a search, but this will override that search.

    .. doctest:: api

        >>> list_names(cfg_path='tests/data/test_config_full.toml')
        ['spam', 'ham', 'tomato'...

    To list the male given names:

    .. doctest:: api

        >>> list_names(gender='male', kind='given')
        ['Noah', 'Liam', 'Jacob'...

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [name.name for name in names]
    return results


def pick_name(
    num_names: int = 1,
    mod: SimpleMod | None = None,
    source: str | None = None,
    culture: str | None = None,
    date: int | None = None,
    gender: str | None = None,
    kind: str | None = None,
    cfg_path: Path | str | None = None,
    db_path: Path | str | None = None
) -> list[str]:
    """Pick random names.

    :param num_names: (Optional.) The number of names
        to create. Defaults to one.
    :param mod: (Optional.) A simple modification
        function for modifying the created names.
        Defaults to no modifying the names.
    :param source: (Optional.) Limit the names
        used to the given :ref:`source<source>`
        Defaults to all sources.
    :param culture: (Optional.) Limit the names
        used to the given :ref:`culture<culture>`
        Defaults to all cultures.
    :param date: (Optional.) Limit the names
        used to the given :ref:`date<date>`
        Defaults to all dates.
    :param gender: (Optional.) Limit the names
        used to the given :ref:`gender<gender>`
        Defaults to all genders.
    :param kind: (Optional.) Limit the names
        used to the given :ref:`kind<kind>`
        Defaults to all kinds.
    :param cfg_path: (Optional.) The path to a
        :ref:`configuration file<config>`.
        Defaults to searching for config files.
    :param db_path: (Optional.) The path to a
        :ref:`names database<names_db>`.
        Defaults to :ref:`searching<db_search>`
        for the database.
    :returns: A :class:`list` object.
    :rtype: list

    :usage:

    To select a name:

    .. testsetup:: pick_name

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import pick_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: pick_name

        >>> pick_name()
        ['Sawyer']

    To pick three names:

    .. doctest:: pick_name

        >>> pick_name(3)
        ['Ethel', 'Harper', 'Erika']

    To force :func:`mkname.pick_name` to use
    a custom names database you built. It will also use
    this database if it's the first found during a search,
    but this will override that search:

    .. doctest:: pick_name

        >>> pick_name(db_path='tests/data/names.db')
        ['ham']

    To force :func:`mkname.pick_name` to use
    a custom configuration you built. It will also use
    this configuration if it's the last found during
    a search, but this will override that search:

    .. doctest:: pick_name

        >>> path = 'tests/data/test_config_full.toml'
        >>> pick_name(cfg_path=path)
        ['spam']

    To pick a name from only male given names:

    .. doctest:: pick_name

        >>> pick_name(gender='male', kind='given')
        ['Clarence']

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [select_name_from_names(names) for _ in range(num_names)]
    results = modify(results, mod)
    return results


# Functions for making names from names.
def build_compound_name_from_names(
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Construct a new game from two randomly selected names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    :usage:

    .. testsetup:: build_compound_name

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import build_compound_name
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: build_compound_name

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names)
        'Teggs'

    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:

    .. doctest:: build_compound_name

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrsvwxz'
        >>> vowels = 'aeiout'
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names, consonants, vowels)
        'Sptomato'
    """
    root_name = select_name_from_names(names)
    mod_name = select_name_from_names(names)
    return compound_names(root_name, mod_name, consonants, vowels)


def build_syllable_name_from_names(
    num_syllables: int,
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Build a name from the syllables of the given names.

    :param num_syllables: The number of syllables in the constructed
        name.
    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    :usage:

    .. testsetup:: build_from_syllables

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import build_from_syllables
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: build_from_syllables

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spameggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggsham', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # The number of syllables in the generated name.
        >>> num_syllables = 3
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names)
        'Atspamegg'

    The function takes into account whether each letter of each
    name is a vowel or a consonant when determining how to split
    the names into syllables. You can affect this by changing which
    letters it treats as consonants or vowels:

    .. doctest:: build_from_syllables

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrtvwxz'
        >>> vowels = 'aeious'
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names, consonants, vowels)
        'Amtomgs'

    """
    base_names = [select_name_from_names(names) for _ in range(num_syllables)]

    result = ''
    for name in base_names:
        syllables = split_into_syllables(name, consonants, vowels)
        index = roll(f'1d{len(syllables)}') - 1
        syllable = syllables[index]
        result = f'{result}{syllable}'
    return result.title()


def select_name_from_names(names: Sequence[Name]) -> str:
    """Select a name from the given list.

    :param names: A list of Name objects to use for constructing
        the new name.
    :return: A :class:str object.
    :rtype: str

    :usage:

    .. testsetup:: select_name

        from unittest.mock import patch
        test_db = 'tests/data/big_names.db'
        patch('mkname.init.get_default_db', return_value=test_db)
        from mkname import select_name
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: select_name

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Generate the name.
        >>> select_name(names)
        'tomato'

    """
    index = roll(f'1d{len(names)}') - 1
    return names[index].name


# Manual name-making functions, old names.
def build_compound_name(
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    msg = (
        'mkname.build_compound_name is deprecated. Use '
        'mkname.build_compound_name_from_names instead.'
    )
    warn(msg, DeprecationWarning)
    return build_compound_name_from_names(names, consonants, vowels)


def build_from_syllables(
    num_syllables: int,
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    msg = (
        'mkname.build_from_syllables is deprecated. Use '
        'mkname.build_syllable_name_from_names instead.'
    )
    warn(msg, DeprecationWarning)
    return build_syllable_name_from_names(
        num_syllables,
        names,
        consonants,
        vowels
    )


def select_name(names: Sequence[Name]) -> str:
    msg = (
        'mkname.select_name is deprecated. Use '
        'mkname.select_name_from_names instead.'
    )
    warn(msg, DeprecationWarning)
    return select_name_from_names(names)


# Common utility functions.
def configure(
    cfg_path: Path | str | None = None,
    db_path: Path | str | None = None
) -> tuple[Section, Path]:
    """Configure based on the invocation arguments.

    :param cfg_path: (Optional.) The path to a
        :ref:`configuration file<config>`.
        Defaults to searching for config files.
    :param db_path: (Optional.) The path to a
        :ref:`names database<names_db>`.
        Defaults to :ref:`searching<db_search>`
        for a names database.
    :returns: A :class:`list` object.
    :rtype: list
    """
    config = get_config(cfg_path)['mkname']
    db_path = get_db(db_path, conf_path=cfg_path)
    return config, db_path


def modify(
    names: Sequence[str],
    mod: SimpleMod | None
) -> list[str]:
    """Use the given simple mod on the names.

    :param names: The names to modify.
    :param mod_key: A simple mod function.
    :returns: A :class:`list` object.
    :rtype: list
    """
    if mod:
        names = [mod(name) for name in names]
    return list(names)
