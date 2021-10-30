"""
test_db
~~~~~~~

Unit tests for the mkname.db module.
"""
import pathlib
import sqlite3
import unittest as ut

from mkname import db
from mkname import model as m


# Test cases.
class ConnectionTestCase(ut.TestCase):
    db_path = 'tests/data/names.db'

    def test_connect(self):
        """When given the path to an sqlite3 database, db.connect_db
        should return a connection to the database.
        """
        # Expected value.
        exp = 'spam'

        # Test data and state.
        query = 'select name from names where id = 1;'

        # Run test and get actual value.
        con = db.connect_db(self.db_path)
        try:
            result = con.execute(query)
            act = result.fetchone()[0]

            # Determine test result.
            self.assertEqual(exp, act)

        # Test cleanup.
        finally:
            con.close()

    def test_connect_no_file(self):
        """If the given file does not exist, db.connect_db should raise
        a ValueError.
        """
        # Set up for expected values.
        filepath = 'tests/data/no_file.db'

        # Expected values.
        exp_ex = ValueError
        exp_msg = f'No database at "{filepath}".'

        # Test data and state.
        path = pathlib.Path(filepath)
        if path.is_file():
            msg = f'Remove file at "{filepath}".'
            raise RuntimeError(msg)

        # Run test and determine results.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            _ = db.connect_db(filepath)

    def test_disconnect(self):
        """When given a database connection, close it."""
        # Expected values.
        exp_ex = sqlite3.ProgrammingError
        exp_msg = 'Cannot operate on a closed database.'

        # Test data and state.
        con = sqlite3.Connection(self.db_path)
        query = 'select name from names where id = 1;'
        result = None

        # Run test.
        db.disconnect_db(con)

        # Determine test result
        with self.assertRaisesRegex(exp_ex, exp_msg):
            result = con.execute(query)

        # Clean up test.
        if result:
            con.close()

    def test_disconnect_with_pending_changes(self):
        """When given a database connection, raise an exception if
        the connection contains uncommitted changes instead of closing
        the connection.
        """
        # Expected values.
        exp_ex = RuntimeError
        exp_msg = 'Connection has uncommitted changes.'

        # Test data and state.
        con = sqlite3.Connection(self.db_path)
        query = "insert into names values (null, 'test', '', '', 0, '', '')"
        _ = con.execute(query)
        result = None

        # Run test and determine result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
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
