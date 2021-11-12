"""
mod
~~~

Functions for modifying names.
"""
import base64 as b64
from functools import partial
from typing import Callable, Mapping, Sequence

from mkname.constants import CONSONANTS, SCIFI_LETTERS, VOWELS
from mkname.dice import roll, seed


# Simple mods.
# Simple mods only require one parameter: the name to modify. Other
# parameters that modify the behavior of the mod can be allowed, but
# must be optional.
def double_vowel(name: str):
    """Double a vowel within the name, like what with that popular
    Star Wars franchise the kids are talking about.
    
    :param name: The name to modify.
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam')
        >>>
        >>> name = 'Bacon'
        >>> double_vowel(name)
        'Baacon'
    """
    letters = VOWELS
    return double_letter(name, letters)


def garble(name: str):
    """Garble some characters in the name by base 64 encoding them.
    
    :param name: The name to modify.
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam')
        >>>
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
    name = f'{name[:index]}{garbled}{name[index + 1:]}'
    return name.capitalize()


def make_scifi(name: str) -> str:
    """A simple version of add_scifi_letters.
    
    :param name: The name to modify.
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam')
        >>>
        >>> name = 'Eggs'
        >>> make_scifi(name)
        'Keggs'
    """
    return add_letters(name)


# Complex mods.
def add_letters(name: str,
                letters: str = SCIFI_LETTERS,
                vowels: str = VOWELS) -> str:
    """Add one of the given letters to a name.
    
    :param name: The name to modify.
    :param letters: The letters to add for the modification.
    :param vowels: The letters to define as vowels.
    
    Usage:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam')
        >>>
        >>> name = 'Eggs'
        >>> add_letters(name)
        'Keggs'
    
    In most cases, the function behaves like the given letters are
    consonants. While it will replace consonants with the letter,
    it will often try to put a letter before or after a vowel.
    This means you can alter the behavior by passing different
    values to the letters and vowels.:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam')
        >>>
        >>> # Treat 'e' as a consonant and don't use 'k'.
        >>> letter = 'qxz'
        >>> vowels = 'aiou'
        >>>
        >>> name = 'Eggs'
        >>> add_letters(name, letter, vowels)
        'Qggs'
    """
    # Determine the letter and where the letter should go in the name.
    letter_index = roll(f'1d{len(letters)}') - 1
    letter = letters[letter_index]
    choice = roll('1d12')
    wild = roll('1d20')
    name = name.casefold()

    # On a 1-5, put the letter at the beginning.
    if choice < 6:
        if name[0] in vowels:
            name = f'{letter}{name}'
        else:
            name = f'{letter}{name[1:]}'

    # On a 6-10, put the letter at the end.
    elif choice < 11:
        if name[-1] in vowels:
            name = f'{name}{letter}'
        else:
            name = f'{name[:-1]}{letter}'

    # On an 11 or 12, replace a random letter in the name.
    elif wild < 20:
        index = roll(f'1d{len(name)}') - 1
        name = f'{name[:index]}{letter}{name[index + 1:]}'

    # On an 11 or 12, if wild is 20, replace multiple letters.
    else:
        len_roll = f'1d{len(name)}'
        count = roll(len_roll)
        indices = [roll(len_roll) - 1 for _ in range(count)]
        for index in indices:
            name = f'{name[:index]}{letter}{name[index + 1:]}'

    name = name.capitalize()
    return name


def compound_names(mod_name: str,
                   root_name: str,
                   consonants: Sequence[str] = CONSONANTS,
                   vowels: Sequence[str] = VOWELS) -> str:
    """Construct a new name using the parts of two names.
    
    :param names: A list of Name objects to use for constructing
        the new name.
    :param consonants: (Optional.) The characters to consider as
        consonants.
    :param vowels: (Optional.) The characters to consider as vowels.
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
        >>> # Generate the name.
        >>> mod_name = 'Spam'
        >>> base_name = 'Eggs'
        >>> compound_names(mod_name, base_name)
        'Speggs'
    
    The function takes into account whether the starting letter of
    each name is a vowel or a consonant when determining how to
    create the name. You can affect this by changing which letters
    it treats as consonants or vowels:
    
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
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam12')
        >>>
        >>> name = 'Bacon'
        >>> double_letter(name)
        'Bacoon'
    
    You can limit the numbers that it will double by passing a string
    of valid letters:
    
        >>> # Seed the RNG to make the example predictable. Don't do
        >>> # this if you want the modification to be random.
        >>> seed('spam12')
        >>>
        >>> # The valid letters to double.
        >>> letters = 'bcn'
        >>>
        >>> name = 'Bacon'
        >>> double_letter(name, letters)
        'Baconn'
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


def translate_characters(name: str,
                         char_map: Mapping[str, str],
                         casefold: bool = True) -> str:
    """Translate characters in the name to different characters.
    
    :param name: The name to modify.
    :param char_map: A translation map for the characters in the
        name. The keys are the original letters and the values are
        the characters to change them to.
    :param casefold: Whether case should be ignored for the transform.
    :return: A :class:str object.
    :rtype: str
    
    Usage:
    
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


# Mod registration.
mods = {
    'double_vowel': double_vowel,
    'garble': garble,
    'make_scifi': make_scifi,
}
