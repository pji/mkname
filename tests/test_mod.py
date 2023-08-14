"""
test_mod
~~~~~~~~

Unit tests for the mkname.mod function.
"""
from mkname import mod


# Core test functions.
def add_letters_test(
    mocker,
    base,
    letter_roll,
    position_roll,
    index_roll=0,
    wild_roll=0,
    count_roll=0,
    index_rolls=(0, 0)
):
    """The common code for the standard test of
    :meth:`mkname.add_scifi_letters`.
    """
    rolls = [
        letter_roll,
        position_roll,
        index_roll,
        wild_roll,
        count_roll,
        *index_rolls,
    ]
    mocker.patch('yadr.roll', side_effect=rolls)
    return mod.add_letters(base)


def add_punctuation_test(mocker, name, rolls, **kwargs):
    """Run a standard add_punctuation test."""
    mocker.patch('yadr.roll', side_effect=rolls)
    return mod.add_punctuation(name, **kwargs)


def simple_mod_test(mocker, mod_fn, base, rolls):
    """Core of the simple modifier (mod) tests."""
    mocker.patch('yadr.roll', side_effect=rolls)
    return mod_fn(base)


# Tests for add_letters.
def test_add_letters_append_letter_when_ends_with_vowel(mocker):
    """When the given base ends with a vowel, the scifi letter should
    be appended to the name if it's added to the end of the name.
    """
    base = 'Steve'
    letter_roll = 4
    position_roll = 6
    result = add_letters_test(mocker, base, letter_roll, position_roll)
    assert result == 'Stevez'


def test_add_letters_prepend_letter_when_starts_with_vowel(mocker):
    """When the given base name starts with a vowel, the scifi letter
    should be prepended to the name if it's added to the front of the
    name.
    """
    base = 'Adam'
    letter_roll = 3
    position_roll = 1
    result = add_letters_test(mocker, base, letter_roll, position_roll)
    assert result == 'Xadam'


def test_add_letters_replace_end_when_ends_with_consonant(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the
    front of the name.
    """
    base = 'Adam'
    letter_roll = 4
    position_roll = 6
    result = add_letters_test(mocker, base, letter_roll, position_roll)
    assert result == 'Adaz'


def test_add_letters_replace_random_letter(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the
    front of the name.
    """
    base = 'Adam'
    result = add_letters_test(
        mocker,
        base,
        letter_roll=1,
        position_roll=11,
        wild_roll=3,
        index_roll=20,
        count_roll=3,
        index_rolls=[1, 3, 3]
    )
    assert result == 'Kdkm'


def test_add_letters_replace_start_when_starts_with_consonant(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the
    front of the name.
    """
    base = 'Steve'
    letter_roll = 3
    position_roll = 1
    result = add_letters_test(mocker, base, letter_roll, position_roll)
    assert result == 'Xteve'


# Tests for add_punctuation.
def test_add_puctuation(mocker):
    """Given a name, add a punctuation mark into the name. It
    capitalizes the first letter and the letter after the
    punctuation mark in the name.
    """
    name = 'spam'
    rolls = [1, 2]
    result = add_punctuation_test(mocker, name, rolls)
    assert result == "S'Pam"


def test_add_puctuation_at_index(mocker):
    """Given an index, add the punctuation at that index."""
    name = 'spam'
    rolls = [3,]
    index = 3
    result = add_punctuation_test(mocker, name, rolls, index=index)
    assert result == 'Spa.M'


def test_add_punctuation_do_not_cap_after_mark(mocker):
    """If False is passed for cap_after, then the letter after the mark
    isn't capitalized.
    """
    name = 'spam'
    rolls = [1,4]
    cap_after = False
    result = add_punctuation_test(mocker, name, rolls, cap_after=cap_after)
    assert result == "Spa'm"


def test_add_punctuation_do_not_cap_before_mark(mocker):
    """If False is passed for cap_before, then the letter before the
    mark isn't capitalized."""
    name = 'spam'
    rolls = [1,2]
    cap_before = False
    result = add_punctuation_test(mocker, name, rolls, cap_before=cap_before)
    assert result == "s'Pam"


def test_add_punctuation_start_of_name(mocker):
    """If the selected position is in front of the name, add the mark to
    the beginning of the name.
    """
    name = 'spam'
    rolls = [2, 1]
    result = add_punctuation_test(mocker, name, rolls)
    assert result == '-Spam'


# Tests for compound_name.
def test_compound_names():
    """Given two names, return a string that combines the two names."""
    a = 'Donatello'
    b = 'Mallory'
    assert mod.compound_names(a, b) == 'Dallory'


# Tests for double_letter.
def test_double_letter_only_given_letters(mocker):
    """If given a string of letters, only double a letter that is in
    that list.
    """
    name = 'Bacon'
    letters = 'aeiou'
    roll = [1,]
    mocker.patch('yadr.roll', side_effect=roll)
    assert mod.double_letter(name, letters) == 'Baacon'


def test_double_letter_given_letters_not_in_name(mocker):
    """If given a string of letters and the name doesn't have any of
    those letters, return the name.
    """
    name = 'Bacon'
    letters = 'kqxz'
    roll = [1,]
    mocker.patch('yadr.roll', side_effect=roll)
    assert mod.double_letter(name, letters) == name


# Test translate_characters.
def test_translate_characters(mocker):
    """Given a mapping that maps characters in the name to different
    characters, return the translated name.
    """
    name = 'donatello'
    char_map = {
        'd': 's',
        'o': 'a',
    }
    roll = [1,]
    mocker.patch('yadr.roll', side_effect=roll)
    assert mod.translate_characters(name, char_map) == 'sanatella'


# Test simple modifiers.
def test_double_vowel(mocker):
    """Given a base name, double_vowel() should double a vowel within
    the name.
    """
    mod_fn = mod.double_vowel
    base = 'Bacon'
    rolls = [1,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Baacon'


def test_garble(mocker):
    """Given a base name, garble() should garble it by converting a
    section in the middle to base64.
    """
    mod_fn = mod.garble
    base = 'Spam'
    rolls = [2,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Scaam'


def test_make_scifi_append_letter_when_ends_with_vowel(mocker):
    """When the given base ends with a vowel, the scifi letter should
    be appended to the name if it's added to the end of the name.
    """
    mod_fn = mod.make_scifi
    base = 'Steve'
    rolls = [4, 6, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Stevez'


def test_make_scifi_prepend_letter_when_starts_with_vowel(mocker):
    """When the given base name starts with a vowel, the scifi letter
    should be prepended to the name if it's added to the front of the
    name.
    """
    mod_fn = mod.make_scifi
    base = 'Adam'
    rolls = [3, 1, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Xadam'


def test_make_scifi_replace_end_when_ends_with_consonant(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the
    front of the name.
    """
    mod_fn = mod.make_scifi
    base = 'Adam'
    rolls = [4, 6, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Adaz'


def test_make_scifi_replace_random_letter(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the
    front of the name.
    """
    mod_fn = mod.make_scifi
    base = 'Adam'
    rolls = [1, 11, 20, 3, 3, 1, 3, 3]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Kdkm'


def test_make_scifi_replace_start_when_starts_with_consonant(mocker):
    """When the given base name starts with a consonant, the scifi
    letter should replace the first letter if it's added to the front
    of the name.
    """
    mod_fn = mod.make_scifi
    base = 'Steve'
    rolls = [3, 1, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == 'Xteve'


def test_vulcanize(mocker):
    """Given a base name, vulcanize() should prefix the name with "T''"."""
    mod_fn = mod.vulcanize
    base = 'Spam'
    rolls = [5, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == "T'Spam"


def test_vulcanize_not_t(mocker):
    """One in six times, the prefix should use a letter other than "T"."""
    mod_fn = mod.vulcanize
    base = 'Spam'
    rolls = [6, 8, 0,]
    result = simple_mod_test(mocker, mod_fn, base, rolls)
    assert result == "Su'Spam"
