"""
test_mod
~~~~~~~~

unit tests for the mkname.mod function.
"""
import unittest as ut
from unittest.mock import patch

from mkname import mod


# Test cases.
class CompoundNamesTestCase(ut.TestCase):
    def test_compound_names(self):
        """Given two names, return a string that combines the two
        names.
        """
        # Expected value.
        exp = 'Dallory'
        
        # Test data and state.
        a = 'Donatello'
        b = 'Mallory'
        
        # Run test.
        act = mod.compound_names(a, b)
        
        # Determine test result.
        self.assertEqual(exp, act)


class SimpleModifiersTestCase(ut.TestCase):
    def _core_modify_test(self, exp, base_name, mod_fn, roll_values):
        """Core of the name modifier (mod) tests."""
        # Test state.
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.side_effect = roll_values

            # Run test.
            act = mod_fn(base_name)

        # Determine test result.
        self.assertEqual(exp, act)

    def addscifiletters_test(self,
                             exp,
                             base_name,
                             letter_roll,
                             position_roll,
                             index_roll=0,
                             wild_roll=0,
                             count_roll=0,
                             index_rolls=(0, 0)):
        """The common code for the standard test of mkname.
        add_scifi_letters().
        """
        roll_values = [
            letter_roll,
            position_roll,
            index_roll,
            wild_roll,
            count_roll,
            *index_rolls,
        ]
        mod_fn = mod.add_scifi_letters
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    def garble_test(self, exp, base_name, index_roll):
        """The common core for tests of garble()."""
        # Test data and state.
        roll_values = [
            index_roll,
        ]
        mod_fn = mod.garble
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

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
