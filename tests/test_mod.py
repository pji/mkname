"""
test_mod
~~~~~~~~

unit tests for the mkname.mod function.
"""
import unittest as ut
from unittest.mock import patch

from mkname import mod


# Test cases.
class AddLetters(ut.TestCase):
    def _core_modify_test(self, exp, base_name, mod_fn, roll_values):
        """Core of the name modifier (mod) tests."""
        # Test state.
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.side_effect = roll_values

            # Run test.
            act = mod_fn(base_name)

        # Determine test result.
        self.assertEqual(exp, act)

    def add_letters_test(self,
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
        mod_fn = mod.add_letters
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    # add_scifi_letters tests.
    def test_addletters_append_letter_when_ends_with_vowel(self):
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
        self.add_letters_test(exp, base, letter_roll, position_roll)

    def test_addletters_prepend_letter_when_starts_with_vowel(self):
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
        self.add_letters_test(exp, base, letter_roll, position_roll)

    def test_addletters_replace_end_when_ends_with_consonant(self):
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
        self.add_letters_test(exp, base, letter_roll, position_roll)

    def test_addletters_replace_random_letter(self):
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
        self.add_letters_test(
            exp,
            base,
            letter_roll,
            position_roll,
            wild_roll,
            index_roll,
            count_roll,
            index_rolls
        )

    def test_addletters_replace_start_when_starts_with_consonant(self):
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
        self.add_letters_test(exp, base, letter_roll, position_roll)


class AddPunctuation(ut.TestCase):
    def add_punctuation_test(self,
                             exp,
                             name,
                             rolls,
                             **kwargs):
        """Run a standard add_punctuation test."""
        # Test data and state.
        kwargs['name'] = name
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.side_effect = rolls

            # Run test.
            act = mod.add_punctuation(**kwargs)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_add_puctuation(self):
        """Given a name, add a punctuation mark into the name. It
        capitalizes the first letter and the letter after the
        punctuation mark in the name.
        """
        exp = "S'Pam"
        name = 'spam'
        rolls = [1, 2]
        self.add_punctuation_test(exp, name, rolls)

    def test_add_puctuation_at_index(self):
        """Given an index, add the punctuation at that index.
        """
        exp = "Spa.M"
        name = 'spam'
        rolls = [3]
        index = 3
        self.add_punctuation_test(exp, name, rolls, index=index)

    def test_add_punctuation_do_not_cap_after_mark(self):
        """If False is passed for cap_after, then the letter after
        the mark isn't capitalized."""
        exp = "Spa'm"
        name = 'spam'
        rolls = [1,4]
        cap_after = False
        self.add_punctuation_test(exp, name, rolls, cap_after=cap_after)

    def test_add_punctuation_do_not_cap_before_mark(self):
        """If False is passed for cap_before, then the letter before
        the mark isn't capitalized."""
        exp = "s'Pam"
        name = 'spam'
        rolls = [1,2]
        cap_before = False
        self.add_punctuation_test(exp, name, rolls, cap_before=cap_before)

    def test_add_punctuation_start_of_name(self):
        """If the selected position is in front of the name,
        add the mark to the beginning of the name.
        """
        exp = '-Spam'
        name = 'spam'
        rolls = [2, 1]
        self.add_punctuation_test(exp, name, rolls)


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


class DoubleLetterTestCase(ut.TestCase):
    def test_double_letter(self):
        """Given a name, select a letter in the name and double it."""
        # Expected value.
        exp = 'Spaam'

        # Test data and state.
        name = 'Spam'
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.return_value = 3

            # Run test.
            act = mod.double_letter(name)

        # Determine test success.
        self.assertEqual(exp, act)

    def test_double_letter_only_given_letters(self):
        """If given a string of letters, only double a letter that
        is in that list."""
        # Expected value.
        exp = 'Baacon'

        # Test data and state.
        name = 'Bacon'
        letters = 'aeiou'
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.return_value = 1

            # Run test.
            act = mod.double_letter(name, letters)

        # Determine test success.
        self.assertEqual(exp, act)

    def test_double_letter_given_letters_not_in_name(self):
        """If given a string of letters and the name doesn't have
        any of those letters, return the name.
        '"""
        # Expected value.
        exp = 'Bacon'

        # Test data and state.
        name = 'Bacon'
        letters = 'kqxz'
        with patch('mkname.mod.roll') as mock_roll:
            mock_roll.return_value = 1

            # Run test.
            act = mod.double_letter(name, letters)

        # Determine test success.
        self.assertEqual(exp, act)


class TranslateLettersTestCase(ut.TestCase):
    def test_translate_characters(self):
        """Given a mapping that maps characters in the name to different
        characters, return the translated name.
        """
        # Expected value.
        exp = 'sanatella'

        # Test data and state.
        name = 'donatello'
        char_map = {
            'd': 's',
            'o': 'a',
        }

        # Run test.
        act = mod.translate_characters(name, char_map)

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

    def double_vowel_test(self, exp, base_name, index_roll):
        """The common core for tests of garble()."""
        # Test data and state.
        roll_values = [
            index_roll,
        ]
        mod_fn = mod.double_vowel
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    def garble_test(self, exp, base_name, index_roll):
        """The common core for tests of garble()."""
        # Test data and state.
        roll_values = [
            index_roll,
        ]
        mod_fn = mod.garble
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    def make_scifi_test(self,
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
        mod_fn = mod.make_scifi
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    def vulcanize_test(self, exp, base_name, roll_values):
        """The common core for tests of garble()."""
        # Test data and state.
        mod_fn = mod.vulcanize
        self._core_modify_test(exp, base_name, mod_fn, roll_values)

    # double_vowel tests.
    def test_double_vowel(self):
        """Given a base name, double_vowel() should double a vowel
        within the name.
        """
        # Expected value.
        exp = 'Baacon'

        # Test data and state.
        base = 'Bacon'
        index_roll = 1

        # Run test and determine result.
        self.double_vowel_test(exp, base, index_roll)

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

    # add_scifi_letters tests.
    def test_make_scifi_append_letter_when_ends_with_vowel(self):
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
        self.make_scifi_test(exp, base, letter_roll, position_roll)

    def test_make_scifi_prepend_letter_when_starts_with_vowel(self):
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
        self.make_scifi_test(exp, base, letter_roll, position_roll)

    def test_make_scifi_replace_end_when_ends_with_consonant(self):
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
        self.make_scifi_test(exp, base, letter_roll, position_roll)

    def test_make_scifi_replace_random_letter(self):
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
        self.make_scifi_test(
            exp,
            base,
            letter_roll,
            position_roll,
            wild_roll,
            index_roll,
            count_roll,
            index_rolls
        )

    def test_make_scifi_replace_start_when_starts_with_consonant(self):
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
        self.make_scifi_test(exp, base, letter_roll, position_roll)

    # vulcanize tests.
    def test_vulcanize(self):
        """Given a base name, vulcanize() should prefix the name
        with "T''".
        """
        # Expected value.
        exp = "T'Spam"

        # Test data and state.
        base = 'Spam'
        roll_values = [5, 0]

        # Run test and determine result.
        self.vulcanize_test(exp, base, roll_values)

    def test_vulcanize_not_t(self):
        """One in six times, the prefix should use a letter other than
        "T".
        """
        # Expected value.
        exp = "Su'Spam"

        # Test data and state.
        base = 'Spam'
        roll_values = [6, 8, 0]

        # Run test and determine result.
        self.vulcanize_test(exp, base, roll_values)
