"""
db
~~

Functions for handling the database for the names package.
"""
from functools import wraps
from pathlib import Path
import sqlite3
from typing import Any, Callable, Union

from mkname.model import Name


# Connection functions.
def connect_db(location: Union[str, Path]) -> sqlite3.Connection:
    """Connect to the database."""
    # Check to make sure the file exists, since sqlite3 fails silently.
    path = Path(location)
    if not path.is_file():
        msg = f'No database at "{path}".'
        raise ValueError(msg)
    
    # Make and return the database connection.
    con = sqlite3.Connection(path)
    return con


def disconnect_db(con: sqlite3.Connection) -> None:
    """Disconnect from the database."""
    if con.in_transaction:
        msg = 'Connection has uncommitted changes.'
        raise RuntimeError(msg)
    con.close()


# Connection decorators.
def makes_connection(fn: Callable) -> Callable:
    """A decorator that manages a database connection for the
    decorated function.
    """
    @wraps(fn)
    def wrapper(given_con: Union[sqlite3.Connection, str, Path] = None,
                *args, **kwargs) -> Any:
        if isinstance(given_con, (str, Path)):
            con = connect_db(given_con)
        elif isinstance(given_con, sqlite3.Connection):
            con = given_con
        result = fn(con, *args, **kwargs)
        if isinstance(given_con, (str, Path)):
            disconnect_db(con)
        return result
    return wrapper


# Serialization/deserialization functions.
@makes_connection
def get_names(con: sqlite3.Connection) -> tuple[Name, ...]:
    """Deserialize the names from the database."""
    query = 'select * from names'
    result = con.execute(query)
    return tuple(Name(*args) for args in result)

@makes_connection
def get_names_by_kind(con: sqlite3.Connection, kind: str) -> tuple[Name, ...]:
    """Deserialize the names from the database."""
    query = 'select * from names where kind == ?'
    params = (kind, )
    result = con.execute(query, params)
    return tuple(Name(*args) for args in result)
