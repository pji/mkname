"""
test_utility
~~~~~~~~~~~~

Unit tests for mkname.utility.
"""
from mkname import utility as u


# Test cases.
def test_determine_cv_pattern():
    """Given a string, return the pattern of consonants and vowels in
    that pattern.
    """
    name = 'william'
    assert u.calc_cv_pattern(name) == 'cvccvvc'


class TestRecapitalize:
    def test_all_caps(self):
        """Given a all capitalized str, :func:`mkname.utility.recapitalize`
        should recapitalize it based on standard English name capitalization
        rules.
        """
        s = 'SPAM'
        result = u.recapitalize(s)
        assert result == s.title()

    def test_mcc(self):
        """Given a str that starts with "mc",
        :func:`mkname.utility.recapitalize`
        should capitalize as "Mc" followed by
        a capital letter.
        """
        s = 'mcspam'
        result = u.recapitalize(s)
        assert result == 'McSpam'


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
