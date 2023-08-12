"""
test_db
~~~~~~~

Unit tests for the mkname.db module.
"""
import pathlib
import sqlite3
import unittest as ut

import pytest

from mkname import db
from mkname import model as m


# Test cases.
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


class SerializationTestCase(ut.TestCase):
    db_path = 'tests/data/names.db'

    def setUp(self):
        self.con = sqlite3.Connection(self.db_path)

    def tearDown(self):
        self.con.close()

    def test_get_names(self):
        """When given a database connection, db.get_names should
        return the names in the database as a tuple.
        """
        # Expected value.
        names = (
            (
                1,
                'spam',
                'eggs',
                'bacon',
                1970,
                'sausage',
                'given'
            ),
            (
                2,
                'ham',
                'eggs',
                'bacon',
                1970,
                'baked beans',
                'given'
            ),
            (
                3,
                'tomato',
                'mushrooms',
                'pancakes',
                2000,
                'sausage',
                'surname'
            ),
            (
                4,
                'waffles',
                'mushrooms',
                'porridge',
                2000,
                'baked beans',
                'given'
            ),
        )
        exp = tuple(m.Name(*args) for args in names)

        # Run test.
        act = db.get_names(self.con)

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_get_names_called_wo_connection(self):
        """When called without a connection, get_names will create
        its own connection.
        """
        # Expected value.
        names = (
            (
                1,
                'spam',
                'eggs',
                'bacon',
                1970,
                'sausage',
                'given'
            ),
            (
                2,
                'ham',
                'eggs',
                'bacon',
                1970,
                'baked beans',
                'given'
            ),
            (
                3,
                'tomato',
                'mushrooms',
                'pancakes',
                2000,
                'sausage',
                'surname'
            ),
            (
                4,
                'waffles',
                'mushrooms',
                'porridge',
                2000,
                'baked beans',
                'given'
            ),
        )
        exp = tuple(m.Name(*args) for args in names)

        # Run test.
        act = db.get_names(self.db_path)

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_get_cultures(self):
        """Given a connection, return the list of unique cultures
        for the names in the database.
        """
        # Expected value.
        exp = (
            'bacon',
            'pancakes',
            'porridge',
        )

        # Run test.
        act = db.get_cultures(self.con)

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_get_kinds(self):
        """Given a connection, return the list of unique kinds
        of names in the database.
        """
        # Expected value.
        exp = (
            'given',
            'surname',
        )

        # Run test.
        act = db.get_kinds(self.con)

        # Determine test results.
        self.assertTupleEqual(exp, act)

    def test_get_names_by_kind(self):
        """When given a database connection and a kind,
        db.get_names_by_kind should return the names of
        that kind in the database as a tuple.
        """
        # Expected value.
        names = (
            (
                3,
                'tomato',
                'mushrooms',
                'pancakes',
                2000,
                'sausage',
                'surname'
            ),
        )
        exp = tuple(m.Name(*args) for args in names)

        # Test data and state.
        kind = 'surname'

        # Run test.
        act = db.get_names_by_kind(self.con, kind)

        # Determine test result.
        self.assertTupleEqual(exp, act)
