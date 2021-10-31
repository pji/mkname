"""
mod
~~~

Functions for modifying names.
"""
import base64 as b64
import random

from mkname.constants import CONSONANTS, SCIFI_LETTERS, VOWELS
from mkname.dice import roll


# Simple mods.
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