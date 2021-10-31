"""
mod
~~~

Functions for modifying names.
"""
import base64 as b64
import random
from typing import Sequence

from mkname.constants import CONSONANTS, SCIFI_LETTERS, VOWELS
from mkname.dice import roll


# Simple mods.
# Simple mods only require one parameter: the name to modify. Other
# parameters that modify the behavior of the mod can be allowed, but
# must be optional.
def add_scifi_letters(name: str,
                      letters: str = SCIFI_LETTERS,
                      vowels: str = VOWELS) -> str:
    """Add a science fiction flare to names by adding letters that
    are more common in science fiction names.
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


def garble(name: str):
    """Garble some characters in the name by base 64 encoding them."""
    index = roll(f'1d{len(name)}') - 1
    char = bytes(name[index], encoding='utf_8')
    garbled_bytes = b64.encodebytes(char)
    garbled = str(garbled_bytes, encoding='utf_8')
    garbled = garbled.replace('=', ' ')
    garbled = garbled.rstrip()
    name = f'{name[:index]}{garbled}{name[index + 1:]}'
    return name.capitalize()


# Complex mods.
def compound_names(mod_name: str,
                   root_name: str,
                   consonants: Sequence[str] = CONSONANTS,
                   vowels: Sequence[str] = VOWELS) -> str:
    """Construct a new name using the parts of two names."""
    def get_change_index(s: str, letters):
        """Detect how many of the starting characters are in the
        given list.
        """
        index = 1
        while index < len(s) and s[index] in letters:
            index += 1
        return index

    name = ''
    
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

    return name[0].upper() + name[1:]
