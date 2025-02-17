"""
mkname
~~~~~~

Tools for building names.
"""
from typing import Sequence

from mkname.constants import *
from mkname.mod import compound_names
from mkname.model import Name
from mkname.utility import roll, split_into_syllables


# Name making functions.
def build_compound_name(
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Construct a new game from two randomly selected names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names)
        'Spomato'

    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrsvwxz'
        >>> vowels = 'aeiout'
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names, consonants, vowels)
        'Sptomato'
    """
    root_name = select_name(names)
    mod_name = select_name(names)
    return compound_names(root_name, mod_name, consonants, vowels)


def build_from_syllables(
    num_syllables: int,
    names: Sequence[Name],
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Build a name from the syllables of the given names.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spameggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggsham', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # The number of syllables in the generated name.
        >>> num_syllables = 3
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names)
        'Shamtomtom'

    The function takes into account whether each letter of each
    name is a vowel or a consonant when determining how to split
    the names into syllables. You can affect this by changing which
    letters it treats as consonants or vowels:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrtvwxz'
        >>> vowels = 'aeious'
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names, consonants, vowels)
        'Gstomtom'
    """
    base_names = [select_name(names) for _ in range(num_syllables)]

    result = ''
    for name in base_names:
        syllables = split_into_syllables(name, consonants, vowels)
        index = roll(f'1d{len(syllables)}') - 1
        syllable = syllables[index]
        result = f'{result}{syllable}'
    return result.title()


def select_name(names: Sequence[Name]) -> str:
    """Select a name from the given list.

    :param names: A list of Name objects to use for constructing
        the new name.
    :return: A :class:str object.
    :rtype: str

    Usage:

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam123456')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', '', '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', '', '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', '', '', 'given'))
        >>>
        >>> # Generate the name.
        >>> select_name(names)
        'eggs'
    """
    index = roll(f'1d{len(names)}') - 1
    return names[index].name
