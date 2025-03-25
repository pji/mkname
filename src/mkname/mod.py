"""
.. _mod_api:

Modifying Names
===============

Functions for modifying names after they've been generated.


.. _simple_mod:

Simple Mods
-----------
Simple mods only require one parameter: the name to modify. This
makes them a bit limited in what they do, but it's easier to call
them from the command line.

.. autofunction:: mkname.double_vowel
.. autofunction:: mkname.garble
.. autofunction:: mkname.make_scifi
.. autofunction:: mkname.vulcanize


Registration
------------
Simple mods can be registered for use in the `mkname.mods`
registry by using the :class:`mkname.simple_mods` decorator.

.. autoclass:: mkname.simple_mod


Complex Mods
------------
Any mod that requires multiple parameters is a complex mod. These
allow more flexible behavior but cannot be used directly through
the `mkname` command line tool.

.. autofunction:: mkname.add_letters
.. autofunction:: mkname.add_punctuation
.. autofunction:: mkname.compound_names
.. autofunction:: mkname.double_letter
.. autofunction:: mkname.translate_characters

"""
import base64 as b64
from collections.abc import Callable, Mapping, Sequence
from functools import partial

from mkname.constants import *
from mkname.model import SimpleMod
from mkname.utility import roll


# Names that will be imported when using *.
__all__ = [
    # Mods.
    'add_letters',
    'add_punctuation',
    'compound_names',
    'double_letter',
    'double_vowel',
    'garble',
    'make_scifi',
    'translate_characters',
    'vulcanize',

    # Mods registration and registry.
    'mods',
    'simple_mod',
]


# Mod registration.
mods: dict[str, SimpleMod] = {}


class simple_mod:
    """A decorator for registering a simple modifies to `mkname.mods`.

    :param key: The `dict` key the mod will be registered under.
    :returns: A :class:`function` object.
    :rtype: function

    :usage:

    You can add a :ref:`simple_mod` you create to the `mkname.mods`
    registery by using :class:`simple_mod` as a decorator for that
    function. You can then access that modifier from the `mkname.mods`
    registry withe its key:

    .. testsetup:: simple_mod

        from mkname.mod import mods, simple_mod

    .. testcode:: simple_mod

        @simple_mod('spam')
        def spam(name):
            return f'SPAM {name} SPAM!'

        mods['spam']('Graham') == 'SPAM Graham SPAM!'

    .. testoutput::

        True

    """
    def __init__(self, key: str) -> None:
        self.key = key

    def __call__(self, fn: SimpleMod) -> SimpleMod:
        mods[self.key] = fn
        return fn


# Simple mods.
@simple_mod('double_vowel')
def double_vowel(name: str):
    """Double a vowel within the name, like what with that popular
    Star Wars™ franchise the kids are talking about.

    :param name: The name to modify.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: double_vowel

        from mkname import double_vowel
        import yadr.operator as yop
        yop.random.seed('spam')

    .. doctest:: double_vowel

        >>> name = 'Bacon'
        >>> double_vowel(name)
        'Baacon'

    """
    letters = VOWELS
    return double_letter(name, letters)


@simple_mod('garble')
def garble(name: str):
    """Garble some characters in the name by base 64 encoding them.

    :param name: The name to modify.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: garble

        from mkname import garble
        import yadr.operator as yop
        yop.random.seed('spam')

    .. doctest:: garble

        >>> name = 'Eggs'
        >>> garble(name)
        'Rqggs'

    """
    # Determine which character should be garbled.
    index = roll(f'1d{len(name)}') - 1

    # Use base64 encoding to turn the character in a sequence of
    # different characters. Base64 only works with bytes.
    char = bytes(name[index], encoding='utf_8')
    garbled_bytes = b64.encodebytes(char)
    garbled = str(garbled_bytes, encoding='utf_8')

    # Transform characters that are valid in base64 but might
    # not make sense for this kind of name.
    garbled = garbled.replace('=', ' ')
    garbled = garbled.rstrip()

    # Add the garbled characters back into the name and return.
    name = _insert_substr(name, garbled, index, replace=True)
    return name.capitalize()


@simple_mod('make_scifi')
def make_scifi(name: str) -> str:
    """A simple version of :func:`mkname.mod.add_scifi_letters`.

    :param name: The name to modify.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: make_scifi

        from mkname import make_scifi
        import yadr.operator as yop
        yop.random.seed('spam')

    .. doctest:: make_scifi

        >>> name = 'Eggs'
        >>> make_scifi(name)
        'Keggs'

    """
    return add_letters(name)


@simple_mod('vulcanize')
def vulcanize(name: str) -> str:
    """Add prefixes to names that are similar to the prefixes seen
    in Vulcan characters in the Star Trek™ franchise.

    :param name: The name to modify.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: vulcanize

        from mkname import vulcanize
        import yadr.operator as yop
        yop.random.seed('spam')

    .. doctest:: vulcanize

        >>> name = 'Bacon'
        >>> vulcanize(name)
        "T'Bacon"

    """
    letter = 't'
    if roll('1d6') > 5:
        letters = 'd k l m n p s su v'.split()
        index = roll(f'1d{len(letters)}') - 1
        letter = letters[index]
    letter = letter.title()
    name = name.title()
    return f"{letter}'{name}"


# Complex mods.
def add_letters(
    name: str,
    letters: str = SCIFI_LETTERS,
    vowels: str = VOWELS
) -> str:
    """Add one of the given letters to a name.

    :param name: The name to modify.
    :param letters: The letters to add for the modification.
    :param vowels: The letters to define as vowels.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: add_letters

        from mkname import add_letters
        import yadr.operator as yop
        yop.random.seed('spam')

    .. doctest:: add_letters

        >>> name = 'Eggs'
        >>> add_letters(name)
        'Keggs'

    In most cases, the function behaves like the given letters are
    consonants. While it will replace consonants with the letter,
    it will often try to put a letter before or after a vowel.
    This means you can alter the behavior by passing different
    values to the letters and vowels.:

    .. doctest:: add_letters

        >>> # Treat 'e' as a consonant and don't use 'k'.
        >>> letter = 'qxz'
        >>> vowels = 'aiou'
        >>> name = 'Eggs'
        >>> add_letters(name, letter, vowels)
        'Eggz'

    """
    # Determine the letter and where the letter should go in the name.
    letter_index = roll(f'1d{len(letters)}') - 1
    letter = letters[letter_index]
    choice = roll('1d12')
    wild = roll('1d20')
    name = name.casefold()
    replace = False

    # On a 1-5, put the letter at the beginning.
    if choice < 6:
        index = 0
        if name[0] not in vowels:
            replace = True
        name = _insert_substr(name, letter, index, replace=replace)

    # On a 6-10, put the letter at the end.
    elif choice < 11:
        index = len(name)
        if name[-1] not in vowels:
            replace = True
            index -= 1
        name = _insert_substr(name, letter, index, replace=replace)

    # On an 11 or 12, replace a random letter in the name.
    elif wild < 20:
        index = roll(f'1d{len(name)}') - 1
        replace = True
        name = _insert_substr(name, letter, index, replace=replace)

    # On an 11 or 12, if wild is 20, replace multiple letters.
    else:
        len_roll = f'1d{len(name)}'
        count = roll(len_roll)
        indices = [roll(len_roll) - 1 for _ in range(count)]
        replace = True
        for index in indices:
            name = _insert_substr(name, letter, index, replace=replace)

    name = name.capitalize()
    return name


def add_punctuation(
    name: str,
    punctuation: Sequence[str] = PUNCTUATION,
    cap_before: bool = True,
    cap_after: bool = True,
    index: int | None = None
) -> str:
    """Add a punctuation mark to the name.

    :param name: The name to modify.
    :param punctuation: (Optional.) The punctuation marks to choose
        from. Defaults to the default set of punctuation marks in
        mkname.constants.
    :param cap_before: (Optional.) Whether the first letter of the
        substring before the punctuation mark should be capitalized.
        Defaults to capitalizing.
    :param cap_after: (Optional.) Whether the first letter after the
        punctuation mark should be capitalized. Defaults to capitalizing.
    :param index: (Optional.) Where to insert the punctuation. Defaults
        to picking an index at random.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: add_punctuation

        from mkname import add_punctuation
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: add_punctuation

        >>> # Seed the RNG to make the example predictable. Don't do
        >>> name = 'eggs'
        >>> add_punctuation(name)
        'E|Ggs'

    The cap_before and cap_after parameters set whether the substrings
    before or after the added punctuation should be capitalized. It
    defaults to capitalizing them both:

    .. doctest:: add_punctuation

        >>> name = 'eggs'
        >>> add_punctuation(name, cap_before=False)
        'eg@Gs'
        >>>
        >>> yop.random.seed('spam123')
        >>> name = 'eggs'
        >>> add_punctuation(name, cap_after=False)
        'E|ggs'

    If you want to specify were the punctuation goes, you can use
    the index parameter. The punctuation parameter also allows you
    to specify what punctuation is allowed:

    .. doctest:: add_punctuation

        >>> name = 'eggs'
        >>> punctuation = ':'
        >>> index = 2
        >>> add_punctuation(name, punctuation, index=index)
        'Eg:Gs'
    """
    # Select the punctuation mark.
    len_mark = len(punctuation)
    mark_index = roll(f'1d{len_mark}') - 1
    mark = punctuation[mark_index]

    # Determine where the mark will go
    if index is None:
        positions = len(name) + 1
        index = roll(f'1d{positions}') - 1

    # Add the mark and return.
    return _insert_substr(name, mark, index, cap_before, cap_after)


def compound_names(
    mod_name: str,
    root_name: str,
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Construct a new name using the parts of two names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. doctest:: mod

        >>> # Generate the name.
        >>> mod_name = 'Spam'
        >>> base_name = 'Eggs'
        >>> compound_names(mod_name, base_name)
        'Speggs'

    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:

    .. doctest:: mod

        >>> # Treat 'e' as a consonant and 'g' as a vowel.
        >>> consonants = 'bcdfhjklmnpqrstvwxze'
        >>> vowels = 'aioug'
        >>>
        >>> # Generate the name.
        >>> mod_name = 'Spam'
        >>> base_name = 'Eggs'
        >>> compound_names(mod_name, base_name, consonants, vowels)
        'Spggs'
    """
    def get_change_index(s: str, letters):
        """Detect how many of the starting characters are in the
        given list.
        """
        index = 1
        while index < len(s) and s[index] in letters:
            index += 1
        return index

    name = ''
    mod_name = mod_name.casefold()
    root_name = root_name.casefold()

    # When both names start with consonants, replace the starting
    # consonants in the root name with the starting consonants of
    # the mod name.
    if root_name[0] not in vowels and mod_name[0] not in vowels:
        index_start = get_change_index(mod_name, consonants)
        index_end = get_change_index(root_name, consonants)
        name = mod_name[0:index_start] + root_name[index_end:]

    # When the root name starts with a vowel but the mod name starts
    # with a consonant, just add the starting consonants of the mod
    # name to the start of the root name
    elif root_name[0] in vowels and mod_name[0] not in vowels:
        index_start = get_change_index(mod_name, consonants)
        name = mod_name[0:index_start] + root_name

    # If both names start with vowels, replace the starting vowels
    # of the root name with the starting vowels of the mod name.
    elif root_name[0] in vowels and mod_name[0] in vowels:
        index_start = get_change_index(mod_name, vowels)
        index_end = get_change_index(root_name, vowels)
        name = mod_name[0:index_start] + root_name[index_end:]

    # If the root name starts with a consonant and the mod name
    # starts with a vowel, add the starting vowels of the mod name
    # to the beginning of the root name.
    elif root_name[0] not in vowels and mod_name[0] in vowels:
        index_start = get_change_index(mod_name, vowels)
        name = mod_name[0:index_start] + root_name

    # This condition shouldn't be possible, so throw an exception
    # for debugging.
    else:
        msg = ('Names must start with either vowels or consonants. '
               f'Names started with {mod_name[0]} and {root_name[0]}')
        raise ValueError(msg)

    return name.title()


def double_letter(name: str, letters: Sequence[str] = '') -> str:
    """Double a letter in the name.

    :param name: The name to modify.
    :param letters: (Optional.) The letters allowed to double. This
        defaults to all letters in the name.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. testsetup:: double_letter

        from mkname import double_letter
        import yadr.operator as yop
        yop.random.seed('spam12345')

    .. doctest:: double_letter

        >>> name = 'Bacon'
        >>> double_letter(name)
        'Baacon'

    You can limit the numbers that it will double by passing a string
    of valid letters:

    .. doctest:: double_letter

        >>> # The valid letters to double.
        >>> letters = 'bcn'
        >>>
        >>> name = 'Bacon'
        >>> double_letter(name, letters)
        'Baccon'

    """
    if letters and not set(name).intersection(set(letters)):
        return name
    if not letters:
        name_len = len(name)
        index = roll(f'1d{name_len}') - 1
    else:
        possibilities = [i for i, c in enumerate(name) if c in letters]
        poss_len = len(possibilities)
        poss_index = roll(f'1d{poss_len}') - 1
        index = possibilities[poss_index]
    return name[0:index] + name[index] + name[index:]


def translate_characters(
    name: str,
    char_map: Mapping[str, str],
    casefold: bool = True
) -> str:
    """Translate characters in the name to different characters.

    :param name: The name to modify.
    :param char_map: A translation map for the characters in the
        name. The keys are the original letters and the values are
        the characters to change them to.
    :param casefold: Whether case should be ignored for the transform.
    :return: A :class:`str` object.
    :rtype: str

    :usage:

    .. doctest:: mod

        >>> # The translation map is a dict.
        >>> char_map = {'s': 'e', 'p': 'g', 'm': 's'}
        >>>
        >>> name = 'spam'
        >>> translate_characters(name, char_map)
        'egas'

    """
    if casefold:
        name = name.casefold()
    char_dict = dict(char_map)
    trans_map = str.maketrans(char_dict)
    return name.translate(trans_map)


# Private utility functions.
def _insert_substr(
    text: str,
    substr: str,
    index: int,
    cap_before: bool = False,
    cap_after: bool = False,
    replace: bool = False
) -> str:
    """Insert a substring into the text.

    :param text: The string to modify.
    :param substr: The substring to insert into the text.
    :param index: The location to insert substr into the text.
    :param cap_before: (Optional.) Whether to capitalize the first
        letter of the section of text before the insertion. Defaults
        to `False`.
    :param cap_after: (Optional.) Whether to capitalize the first
        letter of the section of text after the insertion. Defaults
        to `False`.
    :param replace: (Optional.) Whether to capitalize the first
        letter of the inserted substring. Defaults to `False`.
    :returns: A :class:`str` object.
    :rtype: str
    """
    before = text[0:index]
    if replace:
        index += 1
    after = text[index:]
    if cap_before:
        before = before.title()
    if cap_after:
        after = after.title()
    return f'{before}{substr}{after}'
