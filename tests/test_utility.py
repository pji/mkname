"""
test_utility
~~~~~~~~~~~~

Unit tests for mkname.utility.
"""
import unittest as ut
from unittest.mock import patch

from mkname import utility as u


# Test cases.
class CalcCVPatternTestCase(ut.TestCase):
    def test_determine_cv_pattern(self):
        """Given a string, return the pattern of consonants and vowels
        in that pattern.
        """
        # Expected value.
        exp = 'cvccvvc'

        # Test data and state.
        name = 'william'

        # Run test.
        act = u.calc_cv_pattern(name)

        # Determine test result.
        self.assertEqual(exp, act)


class RollTestCase(ut.TestCase):
    @patch('mkname.utility.yadr.roll', return_value=5)
    def test_return_if_int(self, _):
        """Given YADN that results in an integer being returned from
        yadr.roll, return that integer.
        """
        # Expected value.
        exp = 5

        # Test data and state.
        yadn = '1d4'

        # Run test.
        act = u.roll(yadn)

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.utility.yadr.roll', return_value='spam')
    def test_error_if_string(self, _):
        """Given YADN that results in a string being returned, raise
        a ValueError exception.
        """
        # Expected value.
        exp_ex = ValueError
        exp_msg = ('YADN passed to mkname.utility.roll can only return '
                   'an int. Received type: str')

        # Test data and state.
        yadn = 'eggs'

        # Run test and determine test result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            __ = u.roll(yadn)


class SplitIntoSyllablesTestCase(ut.TestCase):
    def test_split_into_syllables(self):
        """Given a name, return a tuple of substrings that are the
        syllables of the name.
        """
        # Expected value.
        exp = ('wil', 'liam')

        # Test data and state.
        name = 'william'

        # Run test.
        act = u.split_into_syllables(name)

        # Determine test result.
        self.assertTupleEqual(exp, act)

    def test_split_into_syllables_start_w_vowel(self):
        """Given a name, return a tuple of substrings that are the
        syllables of the name even if the name starts with a vowel.
        """
        # Expected value.
        exp = ('al', 'ic', 'e')

        # Test data and state.
        name = 'alice'

        # Run test.
        act = u.split_into_syllables(name)

        # Determine test result.
        self.assertTupleEqual(exp, act)
