"""
test_utility
~~~~~~~~~~~~

Unit tests for mkname.utility.
"""
from mkname import utility as u


# Test for calc_cv_pattern.
def test_determine_cv_pattern():
    """Given a string, return the pattern of consonants and vowels in
    that pattern.
    """
    name = 'william'
    assert u.calc_cv_pattern(name) == 'cvccvvc'


# Tests for split_into_syllables.
def test_split_into_syllables():
    """Given a name, return a tuple of substrings that are the syllables
    of the name.
    """
    name = 'william'
    assert u.split_into_syllables(name) == ('wil', 'liam')


def test_split_into_syllables_start_w_vowel():
    """Given a name, return a tuple of substrings that are the syllables
    of the name even if the name starts with a vowel.
    """
    name = 'alice'
    assert u.split_into_syllables(name) == ('al', 'ic', 'e')
