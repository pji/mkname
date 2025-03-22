"""
core
~~~~

The core public API for :mod:`mkname`.
"""
from pathlib import Path
from typing import Sequence

from mkname import mkname as mn
from mkname.db import get_names
from mkname.init import get_config, get_db
from mkname.mod import mods
from mkname.model import Name, Section, SimpleMod


__all__ = [
    'create_compound_name',
    'create_syllable_name',
    'list_names',
    'pick_name',
]


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


# Core functions.
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

    :usage:

    To generate a compound name:

    .. testsetup:: create_compound_name

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

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [mn.build_compound_name(
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

    :usage:

    To generate a three syllable name:

    .. testsetup:: create_syllable_name

        from mkname import create_syllable_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: create_syllable_name

        >>> num_syllables = 3
        >>> create_syllable_name(num_syllables)
        ['Yerethar']

    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [mn.build_from_syllables(
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

    :usage:

    To list all the names in the names database:

    .. doctest:: api

        >>> list_names()
        ['Noah', 'Liam', 'Jacob', 'Will...
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

    :usage:

    To select a name:

    .. testsetup:: pick_name

        from mkname import pick_name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: pick_name

        >>> pick_name()
        ['Sawyer']
    """
    config, db_path = configure(cfg_path, db_path)
    names = get_names(db_path, source, culture, date, gender, kind)
    results = [mn.select_name(names) for _ in range(num_names)]
    results = modify(results, mod)
    return results
