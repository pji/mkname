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
    def test_build_base_name(self):
        """Given a sequence of names, build_base_name() returns a name
        constructed from the list.
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
        act = mn.build_base_name(names)

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


class ModifyingNames(ut.TestCase):
    def addscifiletters_test(self, exp, base, letter_roll, position_roll,
                             index_roll=0, wild_roll=0, count_roll=0,
                             index_rolls=(0, 0)):
        """The common code for the standard test of mkname.
        add_scifi_letters().
        """
        # Test data and state.
        roll_values = [
            letter_roll,
            position_roll,
            index_roll,
            wild_roll,
            count_roll,
            *index_rolls,
        ]
        with patch('mkname.mkname.roll') as mock_roll:
            mock_roll.side_effect = roll_values

            # Run test.
            act = mn.add_scifi_letters(base)

        # Determine test result.
        self.assertEqual(exp, act)

    def garble_test(self, exp, base, index_roll):
        """The common core for tests of garble()."""
        # Test data and state.
        roll_values = [
            index_roll,
        ]
        with patch('mkname.mkname.roll') as mock_roll:
            mock_roll.side_effect = roll_values

            # Run test.
            act = mn.garble(base)

        # Determine test result.
        self.assertEqual(exp, act)

    # add_scifi_letters tests.
    def test_addscifiletters_append_letter_when_ends_with_vowel(self):
        """When the given base ends with a vowel, the scifi
        letter should be appended to the name if it's added to the
        end of the name.
        """
        # Expected value.
        exp = 'Stevez'

        # Test data and state.
        base = 'Steve'
        letter_roll = 4
        position_roll = 6

        # Run test and determine result.
        self.addscifiletters_test(exp, base, letter_roll, position_roll)

    def test_addscifiletters_prepend_letter_when_starts_with_vowel(self):
        """When the given base name starts with a vowel, the scifi
        letter should be prepended to the name if it's added to the
        front of the name.
        """
        # Expected value.
        exp = 'Xadam'

        # Test data and state.
        base = 'Adam'
        letter_roll = 3
        position_roll = 1

        # Run test and determine result.
        self.addscifiletters_test(exp, base, letter_roll, position_roll)

    def test_addscifiletters_replace_end_when_ends_with_consonant(self):
        """When the given base name starts with a consonant, the scifi
        letter should replace the first letter if it's added to the
        front of the name.
        """
        # Expected value.
        exp = 'Adaz'

        # Test data and state.
        base = 'Adam'
        letter_roll = 4
        position_roll = 6

        # Run test and determine result.
        self.addscifiletters_test(exp, base, letter_roll, position_roll)

    def test_addscifiletters_replace_random_letter(self):
        """When the given base name starts with a consonant, the scifi
        letter should replace the first letter if it's added to the
        front of the name.
        """
        # Expected value.
        exp = 'Kdkm'

        # Test data and state.
        base = 'Adam'
        letter_roll = 1
        position_roll = 11
        index_roll = 3
        wild_roll = 20
        count_roll = 3
        index_rolls = [1, 3, 3]

        # Run test and determine result.
        self.addscifiletters_test(
            exp,
            base,
            letter_roll,
            position_roll,
            wild_roll,
            index_roll,
            count_roll,
            index_rolls
        )

    def test_addscifiletters_replace_start_when_starts_with_consonant(self):
        """When the given base name starts with a consonant, the scifi
        letter should replace the first letter if it's added to the
        front of the name.
        """
        # Expected value.
        exp = 'Xteve'

        # Test data and state.
        base = 'Steve'
        letter_roll = 3
        position_roll = 1

        # Run test and determine result.
        self.addscifiletters_test(exp, base, letter_roll, position_roll)

    # garble tests.
    def test_garble(self):
        """Given a base name, garble() should garble it by converting
        a section in the middle to base64.
        """
        # Expected value.
        exp = 'Scaam'

        # Test data and state.
        base = 'Spam'
        index_roll = 2

        # Run test and determine result.
        self.garble_test(exp, base, index_roll)
