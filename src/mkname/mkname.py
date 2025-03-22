"""
mkname
~~~~~~

This is the core of the public API of :mod:`mkname`.


Making Names
============
The following functions select or create a name from a list of names.

.. autofunction:: mkname.build_compound_name
.. autofunction:: mkname.build_from_syllables
.. autofunction:: mkname.select_name
"""
from collections.abc import Sequence

from mkname.constants import *
from mkname.mod import compound_names
from mkname.model import Name
from mkname.utility import roll, split_into_syllables


# Names that will be imported when using *.
__all__ = [
    'build_compound_name',
    'build_from_syllables',
    'select_name',
]


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

    :usage:

    .. testsetup:: build_compound_name

        from mkname import build_compound_name
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: build_compound_name

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Generate the name.
        >>> build_compound_name(names)
        'Teggs'

    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:

    .. doctest:: build_compound_name

        >>> # Seed the RNG to make this test predictable for this
        >>> # example. Don't do this if you want random names.
        >>> import yadr.operator as yop
        >>> yop.random.seed('spam1')
        >>>
        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
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

    :param num_syllables: The number of syllables in the constructed
        name.
    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str

    :usage:

    .. testsetup:: build_from_syllables

        from mkname import build_from_syllables
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: build_from_syllables

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spameggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggsham', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # The number of syllables in the generated name.
        >>> num_syllables = 3
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names)
        'Atspamegg'

    The function takes into account whether each letter of each
    name is a vowel or a consonant when determining how to split
    the names into syllables. You can affect this by changing which
    letters it treats as consonants or vowels:

    .. doctest:: build_from_syllables

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Treat 't' as a vowel rather than a consonant.
        >>> consonants = 'bcdfghjklmnpqrtvwxz'
        >>> vowels = 'aeious'
        >>>
        >>> # Generate the name.
        >>> build_from_syllables(num_syllables, names, consonants, vowels)
        'Amtomgs'

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

    :usage:

    .. testsetup:: select_name

        from mkname import select_name
        from mkname.model import Name
        import yadr.operator as yop
        yop.random.seed('spam123')

    .. doctest:: select_name

        >>> # The list of names needs to be Name objects.
        >>> names = []
        >>> names.append(Name(1, 'spam', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(2, 'eggs', 'url', '', 1970, '', 'given'))
        >>> names.append(Name(3, 'tomato', 'url', '', 1970, '', 'given'))
        >>>
        >>> # Generate the name.
        >>> select_name(names)
        'tomato'

    """
    index = roll(f'1d{len(names)}') - 1
    return names[index].name
