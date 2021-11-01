"""
test_mkname
~~~~~~~~~~~
"""
import unittest as ut
from unittest.mock import patch
from typing import Mapping

from mkname import mkname as mn
from mkname import dice as r


# Test cases.
class BuildingNamesTestCase(ut.TestCase):
    def test_build_compound_name(self):
        """Given a sequence of names, build_compound_name() returns a
        name constructed from the list.
        """
        # Expected value.
        exp = 'Dallory'

        # Test data and state.
        r._seed('spam12')
        names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]

        # Run test.
        act = mn.build_compound_name(names)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_build_from_syllables(self):
        """Given a sequence of names, return a name build from one
        syllable from each name.
        """
        # Expected value.
        exp = 'liamjosnoah'

        # Test data and state.
        names = ('william', 'joseph', 'noah')
        rolls = (2, 1, 1)
        with patch('mkname.mkname.roll') as mock_roll:
            mock_roll.side_effect = rolls

            # Run test.
            act = mn.build_from_syllables(names)

        # Determine test results.
        self.assertEqual(exp, act)

    def test_select_random_name(self):
        """Given a list of names, return a random name."""
        # Expected value.
        exp = 'Donatello'

        # Test data and state.
        r._seed('spam12')
        names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]

        # Run test.
        act = mn.select_name(names)

        # Determine test result.
        self.assertEqual(exp, act)


class InitializationTestCase(ut.TestCase):
    def assertConfigEqual(self, a: Mapping, b: Mapping) -> None:
        """Assert that two ParserConfig objects are equal."""
        a_keylist = list(a.keys())
        b_keylist = list(b.keys())
        self.assertListEqual(a_keylist, b_keylist)
        for key in a:
            if not isinstance(a[key], str):
                self.assertConfigEqual(a[key], b[key])
            else:
                self.assertEqual(a[key], b[key])

    def test_load_config(self):
        """When called, load_config() should return a mapping that
        contains the mkname configuration from the given configuration
        file.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        config_path = 'tests/data/test_load_config.conf'

        # Run test.
        act = mn.load_config(config_path)

        # Determine test result.
        self.assertConfigEqual(exp, act)
