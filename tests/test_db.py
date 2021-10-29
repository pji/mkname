"""
test_db
~~~~~~~

Unit tests for the mkname.db module.
"""
import sqlite3
import unittest as ut

from mkname import db
from mkname import model as m


# Test cases.
class DeserializationTestCase(ut.TestCase):
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
