"""
test_db
~~~~~~~

Unit tests for the mkname.db module.
"""
import pathlib
import sqlite3

import pytest

from mkname import db
from mkname import model as m


# Fixtures
@pytest.fixture
def con():
    """Manage a test database connection."""
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    yield con
    con.close()


# Connection test cases.
def test_connect():
    """When given the path to an sqlite3 database, db.connect_db
    should return a connection to the database.
    """
    # Test data and state.
    db_path = 'tests/data/names.db'
    query = 'select name from names where id = 1;'

    # Run test.
    con = db.connect_db(db_path)
    try:
        selected = con.execute(query)
        result = selected.fetchone()
    finally:
        con.close()

    # Determine test result.
    assert result == ('spam',)


def test_connect_no_file():
    """If the given file does not exist, db.connect_db should raise
    a ValueError.
    """
    # Test data and state.
    db_path = 'tests/data/no_file.db'
    path = pathlib.Path(db_path)
    if path.is_file():
        msg = f'Remove file at "{path}".'
        raise RuntimeError(msg)

    # Run test and determine results.
    with pytest.raises(ValueError, match=f'No database at "{path}".'):
        _ = db.connect_db(path)


def test_disconnect():
    """When given a database connection, close it."""
    # Test data and state.
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    query = 'select name from names where id = 1;'
    result = None

    # Run test.
    db.disconnect_db(con)

    # Determine test result
    with pytest.raises(
        sqlite3.ProgrammingError,
        match='Cannot operate on a closed database.'
    ):
        result = con.execute(query)

    # Clean up test.
    if result:
        con.close()


def test_disconnect_with_pending_changes():
    """When given a database connection, raise an exception if
    the connection contains uncommitted changes instead of closing
    the connection.
    """
    # Test data and state.
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    query = "insert into names values (null, 'test', '', '', 0, '', '')"
    _ = con.execute(query)
    result = None

    # Run test and determine result.
    with pytest.raises(
        RuntimeError,
        match='Connection has uncommitted changes.'
    ):
        db.disconnect_db(con)


# Serialization test cases.
def test_get_names(con):
    """When given a database connection, db.get_names should
    return the names in the database as a tuple.
    """
    # Expected value.
    assert db.get_names(con) == (
        m.Name(
            1,
            'spam',
            'eggs',
            'bacon',
            1970,
            'sausage',
            'given'
        ),
        m.Name(
            2,
            'ham',
            'eggs',
            'bacon',
            1970,
            'baked beans',
            'given'
        ),
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
        m.Name(
            4,
            'waffles',
            'mushrooms',
            'porridge',
            2000,
            'baked beans',
            'given'
        ),
    )


def test_get_names_called_wo_connection():
    """When called without a connection, get_names will create
    its own connection.
    """
    db_path = 'tests/data/names.db'
    assert db.get_names(db_path) == (
        m.Name(
            1,
            'spam',
            'eggs',
            'bacon',
            1970,
            'sausage',
            'given'
        ),
        m.Name(
            2,
            'ham',
            'eggs',
            'bacon',
            1970,
            'baked beans',
            'given'
        ),
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
        m.Name(
            4,
            'waffles',
            'mushrooms',
            'porridge',
            2000,
            'baked beans',
            'given'
        ),
    )


def test_get_cultures(con):
    """Given a connection, return the list of unique cultures
    for the names in the database.
    """
    # Expected value.
    assert db.get_cultures(con) == (
        'bacon',
        'pancakes',
        'porridge',
    )


def test_get_cultures(con):
    """Given a connection, return the list of unique kinds of names
    in the database.
    """
    assert db.get_kinds(con) == (
        'given',
        'surname',
    )


def test_get_names_by_kind(con):
    """When given a database connection and a kind,
    db.get_names_by_kind should return the names of
    that kind in the database as a tuple.
    """
    # Expected value.
    kind = 'surname'
    assert db.get_names_by_kind(con, kind) == (
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
    )
