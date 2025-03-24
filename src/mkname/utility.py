"""
utility
~~~~~~~

General utility functions for :mod:`mkname`.

.. autofunction:: mkname.utility.calc_cv_pattern
.. autofunction:: mkname.utility.recapitalize
.. autofunction:: mkname.utility.split_into_syllables
.. autofunction:: mkname.utility.roll

"""
from collections.abc import Sequence

import yadr

from mkname.constants import CONSONANTS, VOWELS


# Random number generation.
def roll(yadn: str) -> int:
    """Provide a random number based on the given dice notation.

    :param yadn: The dice to roll expressed as a YADN string.
    :returns: An :class:`int` object.
    :rtype: int
    """
    result = yadr.roll(yadn)

    # `mkname` only uses `yadr` to generate `int`. If YADN that
    # generates something other than an `int` gets here, puke.
    if not isinstance(result, int):
        rtype = type(result).__name__
        msg = (
            'YADN passed to mkname.utility.roll can only return '
            f'an int. Received type: {rtype}'
        )
        raise ValueError(msg)

    return result


# Word analysis functions.
def calc_cv_pattern(
    name: str,
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> str:
    """Determine the pattern of consonants and vowels in the name.

    :param name: The name to inspect.
    :param consonants: (Optional.) The characters to treat as
        consonants. Defaults to a string containing every standard
        English consonant.
    :param vowels: (Optional.) The characters to treat as vowels.
        Defaults to a string containing every standard English
        vowel, including `y`.
    :returns: A :class:`str` object.
    :rtype: str

    :usage:

    To determine which characters in "spammy eggs" are consonants and
    which are vowels:

        >>> name = 'spammy eggs'
        >>> calc_cv_pattern(name)
        'ccvccvxvccc'

    """
    name = name.casefold()
    pattern = ''
    for char in name:
        if char in consonants:
            pattern += 'c'
        elif char in vowels:
            pattern += 'v'
        else:
            pattern += 'x'
    return pattern


# Word manipulation functions.
def recapitalize(s: str) -> str:
    """Recapitalize the string based on common name patterns.

    :param s: The string to recapitalize.
    :returns: A :class:`str` object.
    :rtype: str

    :usage:

    To recapitalize a string:

        >>> name = 'GRAHAM'
        >>> recapitalize(name)
        'Graham'

    It will also recognize the "Mc" pattern at the beginning of names
    and capitalize accordingly:

        >>> name = 'mccoy'
        >>> recapitalize(name)
        'McCoy'

    """
    normal = s.casefold()
    if normal.startswith('mc'):
        result = 'Mc' + normal[2:].title()
    else:
        result = normal.title()
    return result


def split_into_syllables(
    name: str,
    consonants: Sequence[str] = CONSONANTS,
    vowels: Sequence[str] = VOWELS
) -> tuple[str, ...]:
    """Split a name into syllables. Sort of. It's a simple and very
    inaccurate algorithm.

    :param name: The name to inspect.
    :param consonants: (Optional.) The characters to treat as
        consonants. Defaults to a string containing every standard
        English consonant.
    :param vowels: (Optional.) The characters to treat as vowels.
        Defaults to a string containing every standard English
        vowel, including `y`.
    :returns: A :class:`tuple` object.
    :rtype: tuple

    :usage:

    Split the word "tomato" into "syllables." These
    won't match the actual syllables for the word.
    It just breaks the work into syllable-like chunks:

        >>> name = 'tomato'
        >>> split_into_syllables(name)
        ('tom', 'at', 'o')

    """
    # Find the locations of all vowels in the word.
    pattern = calc_cv_pattern(name, consonants, vowels)
    vowel_indices = [i for i, char in enumerate(pattern) if char == 'v']

    # If there are one or zero vowels in the word, the word is
    # just one syllable.
    if len(vowel_indices) < 2:
        return (name, )

    # If there are two or more vowels, split the word into chunks.
    else:
        slices = []
        last_location = vowel_indices[0]
        last_split = 0

        # Iterate through the vowels in the word, storing the start
        # and stop indices for each chunk.
        for location in vowel_indices[1:]:
            if location - last_location <= 1:
                last_location = location
                continue
            diff = ((location - last_location) // 2) + 1
            split = last_location + diff
            slices.append((last_split, split))
            last_location = location
            last_split = split

        # After going through all the vowels, add the final index
        # of the word for the final chunk.
        else:
            split = len(name) + 1
            slices.append((last_split, split))

    # Return the chunks in a tuple.
    return tuple(name[s:e] for s, e in slices)
