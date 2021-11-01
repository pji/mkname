"""
test_utility
~~~~~~~~~~~~

Unit tests for mkname.utility.
"""
import unittest as ut

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
