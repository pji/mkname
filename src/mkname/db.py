"""
db
~~

Functions for handling the database for the names package.


Read Data
=========
The following functions all pull data out of the database. While you
can manually pass a database connection to these functions if you
ever need to, they will create their own connection if you don't.

.. autofunction:: mkname.get_names
.. autofunction:: mkname.get_names_by_kind
.. autofunction:: mkname.get_cultures
.. autofunction:: mkname.get_genders
.. autofunction:: mkname.get_kinds


Create Database
===============
The following functions create new databases.

.. autofunction:: mkname.duplicate_db
.. autofunction:: mkname.create_empty_db


Connecting to the Database
==========================
The "read" functions detailed above use the
:func:`mkname.db.makes_connection` decorator to
automatically create database connections.

.. autofunction:: mkname.db.makes_connection.

However, if you want to make a manual connection to the database, you
can use the following functions to open and close the connection.

.. autofunction:: mkname.connect_db
.. autofunction:: mkname.disconnect_db

"""
import sqlite3
from collections.abc import Callable, Sequence
from functools import wraps
from pathlib import Path
from typing import Any, Union

from mkname import init
from mkname.constants import MSGS
from mkname.exceptions import DefaultDatabaseWriteError, IDCollisionError
from mkname.model import Name


# Names that will be imported when using *.
__all__ = [
    'duplicate_db',
    'get_cultures',
    'get_genders',
    'get_kinds',
    'get_names',
    'get_names_by_kind',
]


# Connection functions.
def connect_db(location: Union[str, Path]) -> sqlite3.Connection:
    """Connect to the database.

    :param location: The path to the database file.
    :return: A :class:sqlite3.Connection object.
    :rtype: sqlite3.Connection

    Usage:

        >>> loc = 'src/mkname/data/names.db'
        >>> query = 'select name from names where id = 1;'
        >>> con = connect_db(loc)
        >>> result = con.execute(query)
        >>> tuple(result)
        (('Liam',),)
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

    See connect_db() for usage.
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

    Usage:

        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_cultures(loc)               # doctest: +ELLIPSIS
        ('bacon', 'pancakes', 'porridge')
    """
    query = 'select distinct culture from names'
    return _run_query_for_single_column(con, query)


@makes_connection
def get_genders(con: sqlite3.Connection) -> tuple[str, ...]:
    """Get a list of unique genders in the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    Usage:

        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_genders(loc)                  # doctest: +ELLIPSIS
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

    Usage:

        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_kinds(loc)                  # doctest: +ELLIPSIS
        ('given', 'surname')
    """
    query = 'select distinct kind from names'
    return _run_query_for_single_column(con, query)


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


@makes_connection
def get_names(con: sqlite3.Connection) -> tuple[Name, ...]:
    """Deserialize the names from the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    Usage:

        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> get_names(loc)                  # doctest: +ELLIPSIS
        (Name(id=1, name='spam', source='eggs', ... kind='given'))
    """
    query = 'select * from names'
    result = con.execute(query)
    return tuple(Name(*args) for args in result)


@makes_connection
def get_names_by_kind(con: sqlite3.Connection, kind: str) -> tuple[Name, ...]:
    """Deserialize the names from the database.

    :param con: The connection to the database. It defaults to
        creating a new connection to the default database if no
        connection is passed.
    :param kind: The kind of names to return. By default, this is
        either 'given' or 'surname', but if you have a custom
        database you can add other types.
    :return: A :class:`tuple` of :class:`Name` objects.
    :rtype: tuple

    Usage:

        >>> # @makes_connection allows you to pass the path of
        >>> # the database file rather than a connection.
        >>> loc = 'tests/data/names.db'
        >>> kind = 'given'
        >>> get_names_by_kind(loc, kind)    # doctest: +ELLIPSIS
        (Name(id=1, name='spam', source='eggs', ... kind='given'))
    """
    query = 'select * from names where kind == ?'
    params = (kind, )
    result = con.execute(query, params)
    return tuple(Name(*args) for args in result)


# Create functions.
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


# Update functions.
@protects_connection
def add_name_to_db(
    con: sqlite3.Connection,
    name: Name,
    update: bool = False
) -> None:
    """Add a name to the given database.

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
    """Add multiple names to the database.

    .. warning:
        This function will not update the default database by default.
        You can still explicitly point it to the default database, but
        that is probably a bad idea because updates will be lost when
        the package is updated.
    """
    for name in names:
        add_name_to_db(con, name, update)
