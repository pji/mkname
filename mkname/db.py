"""
db
~~

Functions for handling the database for the names package.
"""
import sqlite3

from mkname.model import Name


def get_names(con: sqlite3.Connection) -> tuple[Name, ...]:
    """Deserialize the names from the database."""
    query = 'select * from names'
    result = con.execute(query)
    return tuple(Name(*args) for args in result)
