"""
.. testsetup::

    from mkname import *
    from mkname.db import connect_db, disconnect_db


.. _db_api:

Data Gathering
==============
The following is a description of the API for working directly
with a names database.


.. _db_read:

Read Data
---------
The following functions all read records in the database. While you
can manually pass a database connection to these functions if you
ever need to, they will create their own connection if you don't.

.. autofunction:: mkname.get_cultures
.. autofunction:: mkname.get_dates
.. autofunction:: mkname.get_genders
.. autofunction:: mkname.get_kinds
.. autofunction:: mkname.get_names
.. autofunction:: mkname.get_names_by_kind
.. autofunction:: mkname.get_sources


.. _db_admin:

Database Administration
-----------------------
The following functions are used to create and update data in a
:ref:`names database <names_db>` or otherwise administer those
databases.


.. _db_connect:

Connecting to the Database
^^^^^^^^^^^^^^^^^^^^^^^^^^
For the most part, functions that need to connect to a names
database should manage that connection through one of these
decorators. Specifically, anything that just reads should use
:func:`mkname.db.makes_connection`, and anything that needs to
create, update, or delete should use
:func:`mkname.db.protects_connection`.

.. autofunction:: mkname.db.makes_connection
.. autofunction:: mkname.db.protects_connection

However, if you want to make a manual connection to the database, you
can use the following functions to open and close the connection.

.. autofunction:: mkname.db.connect_db
.. autofunction:: mkname.db.disconnect_db


.. _db_create:

Create and Update Data
^^^^^^^^^^^^^^^^^^^^^^
The following functions will create and update records in the
database. While you can manually pass a database connection to
these functions if you ever need to, they will create their own
connection if you don't.

.. warning:
    These functions are only intended to be used by :mod:`mkname`.
    Other code should use the functions provided by :mod:`mkname.tools`.

.. warning:
    These functions attempt to prevent changes to the :ref:`default_db`
    to avoid unexpected behavior when the package is updated. It's not
    foolproof, and you can cause yourself a lot of problems if you
    want to.

.. autofunction:: mkname.db.get_max_id
.. autofunction:: mkname.db.add_name_to_db
.. autofunction:: mkname.db.add_names_to_db


.. _db_creation:

Database Creation
^^^^^^^^^^^^^^^^^
The following functions create new databases.

.. warning:
    These functions are only intended to be used by :mod:`mkname`.
    Other code should use the functions provided by :mod:`mkname.tools`.

.. autofunction:: mkname.db.duplicate_db
.. autofunction:: mkname.db.create_empty_db

"""
import sqlite3
from collections.abc import Callable, Sequence
from functools import wraps
from pathlib import Path
from typing import Any, Union
from warnings import warn

from mkname import init
from mkname.constants import MSGS
from mkname.exceptions import DefaultDatabaseWriteError, IDCollisionError
from mkname.model import Name


# Names that will be imported when using *.
__all__ = [
    'get_cultures',
    'get_dates',
    'get_genders',
    'get_kinds',
    'get_names',
    'get_names_by_kind',
    'get_sources',
]


# Connection functions.
def connect_db(location: Union[str, Path]) -> sqlite3.Connection:
    """Connect to the database.

    :param location: The path to the database file.
    :return: A :class:sqlite3.Connection object.
    :rtype: sqlite3.Connection

    :usage:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> query = 'select name from names where id = 1;'
        >>> con = connect_db(loc)
        >>> result = con.execute(query)
        >>> tuple(result)
        (('spam',),)
        >>> disconnect_db(con)

    """
    # Check to make sure the file exists, since sqlite3 fails silently.
    path = Path(location)
    if not path.is_file():
        msg = f'No database at "{path}".'
        raise ValueError(msg)

    # Make and return the database connection.
    con = sqlite3.Connection(path)
    return con


def disconnect_db(
    con: sqlite3.Connection,
    override_commit: bool = False
) -> None:
    """Disconnect from the database.

    :param con: A database connection.
    :param override_commit: (Optional.) Whether to override errors
        due to uncommitted changes. Defaults to `False`.
    :return: None.
    :rtype: :class:NoneType

    See :func:`mkname.db.connect_db` for usage.
    """
    if con.in_transaction and not override_commit:
        msg = 'Connection has uncommitted changes.'
        raise RuntimeError(msg)
    con.close()


# Connection decorators.
def makes_connection(fn: Callable) -> Callable:
    """A decorator that manages a database connection for the
    decorated function.
    """
    @wraps(fn)
    def wrapper(
        given_con: Union[sqlite3.Connection, str, Path, None] = None,
        *args, **kwargs
    ) -> Any:
        if isinstance(given_con, (str, Path)):
            con = connect_db(given_con)
        elif isinstance(given_con, sqlite3.Connection):
            con = given_con
        else:
            default_path = init.get_db()
            con = connect_db(default_path)
        result = fn(con, *args, **kwargs)
        if isinstance(given_con, (str, Path)):
            disconnect_db(con)
        return result
    return wrapper


def protects_connection(fn: Callable) -> Callable:
    """A decorator that manages a database connection for the
    decorated function and prevents implicit connection to the
    default database.

    .. note:
        This is intended as a guard against accidental changes to
        the default database. It is not intended as a security control.
    """
    @wraps(fn)
    def wrapper(
        given_con: Union[sqlite3.Connection, str, Path, None] = None,
        *args, **kwargs
    ) -> Any:
        if isinstance(given_con, (str, Path)):
            con = connect_db(given_con)
        elif isinstance(given_con, sqlite3.Connection):
            con = given_con
        else:
            msg = 'Must explicitly connect to a DB for this action.'
            raise DefaultDatabaseWriteError(msg)
        result = fn(con, *args, **kwargs)
        if isinstance(given_con, (str, Path)):
            disconnect_db(con)
        return result
    return wrapper


# Private query functions.
def _run_query_for_single_column(
    con: sqlite3.Connection,
    query: str,
) -> tuple[str, ...]:
    """Run the query and return the results."""
    result = con.execute(query)
    return tuple(text[0] for text in result)


# Read functions.
@makes_connection
def get_cultures(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique cultures in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_cultures(loc)
        ('bacon', 'pancakes', 'porridge')

    """
    query = 'select distinct culture from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_dates(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique dates in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_dates(loc)
        (1970, 2000)

    """
    query = 'select distinct date from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_genders(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique genders in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_genders(loc)
        ('sausage', 'baked beans')

    """
    query = 'select distinct gender from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_kinds(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique kinds in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_kinds(loc)
        ('given', 'surname')

    """
    query = 'select distinct kind from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_names(
    con: sqlite3.Connection,
    source: str | None = None,
    culture: str | None = None,
    date: int | None = None,
    gender: str | None = None,
    kind: str | None = None,
) -> tuple[Name, ...]:
    """Deserialize the names from the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :param source: (Optional.) A filtering value for the `source`
        field. Defaults to a wildcard.
    :param culture: (Optional.) A filtering value for the `culture`
        field. Defaults to a wildcard.
    :param date: (Optional.) A filtering value for the `date`
        field. Defaults to a wildcard.
    :param gender: (Optional.) A filtering value for the `gender`
        field. Defaults to a wildcard.
    :param kind: (Optional.) A filtering value for the `kind`
        field. Defaults to a wildcard.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_names(loc)
        (Name(id=1, name='spam', source='eggs', ... kind='given'))

    """
    query = (
        'SELECT * FROM names WHERE '
        'source LIKE :source AND '
        'culture LIKE :culture AND '
        'date LIKE :date AND '
        'gender LIKE :gender AND '
        'kind LIKE :kind;'
    )
    params = {
        'source': source if source is not None else '%',
        'culture': culture if culture is not None else '%',
        'date': date if date is not None else '%',
        'gender': gender if gender is not None else '%',
        'kind': kind if kind is not None else '%',
    }
    result = con.execute(query, params)
    return tuple(Name(*args) for args in result)


@makes_connection
def get_names_by_kind(con: sqlite3.Connection, kind: str) -> tuple[Name, ...]:
    """Deserialize the names from the database.

    .. warning:
        This function is deprecated. If you need to get the names
        of a certain kind from the database, you should use the
        `kind` parameter of :func:`mkname.db.get_name` instead.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :param kind: The kind of names to return. By default, this is
        either 'given' or 'surname', but if you have a custom
        database you can add other types.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> kind = 'given'
        >>> get_names_by_kind(loc, kind)
        (Name(id=1, name='spam', source='eggs', ... kind='given'))

    """
    # Provide a deprecation warning.
    msg = 'Use the "kind" parameter of get_names instead.'
    warn(msg, DeprecationWarning)

    query = 'select * from names where kind == ?'
    params = (kind, )
    result = con.execute(query, params)
    return tuple(Name(*args) for args in result)


@makes_connection
def get_sources(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique sources in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    :usage:

    @makes_connection allows you to pass the path of
    the database file rather than a connection:

    .. doctest::

        >>> loc = 'tests/data/names.db'
        >>> get_sources(loc)
        ('eggs', 'mushrooms')

    """
    query = 'select distinct source from names'
    return _run_query_for_single_column(con, query)


# Create and update functions.
@protects_connection
def add_name_to_db(
    con: sqlite3.Connection,
    name: Name,
    update: bool = False
) -> None:
    """Add a name to the given database. If the name has the same
    ID as a name already in the database, update the values in the
    database to match the values for the given name.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :returns: `None`.
    :rtype: NoneType

    .. warning:
        This function will not update the default database by default.
        You can still explicitly point it to the default database, but
        that is probably a bad idea because updates will be lost when
        the package is updated.
    """
    q = (
        'INSERT INTO names '
        '(id, name, source, culture, date, gender, kind) '
        'VALUES(:id, :name, :source, :culture, :date, :gender, :kind)'
    )

    try:
        cur = con.execute(q, name.asdict())
        con.commit()
    except sqlite3.IntegrityError:
        if not update:
            msg = MSGS['en']['id_collision'].format(id=name.id)
            raise IDCollisionError(msg)
        else:
            q = (
                'UPDATE names '
                'SET name = :name, '
                'source = :source, '
                'culture = :culture, '
                'date = :date, '
                'gender = :gender, '
                'kind = :kind '
                'WHERE id = :id'
            )
            cur = con.execute(q, name.asdict())
            con.commit()


@protects_connection
def add_names_to_db(
    con: sqlite3.Connection,
    names: Sequence[Name],
    update: bool = False
) -> None:
    """Add multiple names to the database. If any of those names have
    the same ID as names already existing in the database, update the
    values for those names in the database to the values for the given
    names.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :returns: `None`.
    :rtype: NoneType

    .. warning:
        This function will not update the default database by default.
        You can still explicitly point it to the default database, but
        that is probably a bad idea because updates will be lost when
        the package is updated.
    """
    for name in names:
        add_name_to_db(con, name, update)


# Administration functions.
def duplicate_db(dst_path: Path | str) -> None:
    """Create a duplicate of the `names.db` database.

    :param dst_path: The path to copy the database into.
    :return: `None`.
    :rtype: NoneType
    """
    # Creating a connection to a non-existant database creates a
    # new database.
    dst_con = sqlite3.Connection(dst_path)

    # Create the connection to the original names DB.
    src_path = init.get_default_db()
    src_con = connect_db(src_path)

    # Copy the names DB into the new DB.
    src_con.backup(dst_con)

    # Close the database connections.
    src_con.close
    dst_con.close()


def create_empty_db(path: Path | str) -> None:
    """Create an empty names database.

    :param path: Where to create the database.
    :returns: `None`.
    :rtype: NoneType
    """
    query = (
        'CREATE TABLE names(\n'
        '    id          integer primary key autoincrement,\n'
        '    name        char(64),\n'
        '    source      char(128),\n'
        '    culture     char(64),\n'
        '    date        integer,\n'
        '    gender      char(64),\n'
        '    kind        char(16)\n'
        ')\n'
    )
    con = sqlite3.Connection(path)
    con.execute(query)
    con.close()


@makes_connection
def get_max_id(con: sqlite3.Connection) -> int:
    """Get the highest ID in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: An :class:`int` object.
    :rtype: tuple
    """
    q = 'SELECT id FROM names ORDER BY id DESC LIMIT 1'
    cur = con.execute(q)
    result = cur.fetchone()
    if result is None:
        return 0
    else:
        return result[0]
