"""
mkname
~~~~~~

Tools for building names.
"""
import configparser
import random
from typing import Mapping, Sequence

from mkname.constants import CONSONANTS, VOWELS
from mkname.dice import roll


# Initialization functions.
def load_config(filepath: str) -> Mapping:
    """Load the configuration."""
    config = configparser.ConfigParser()
    config.read(filepath)
    return config['mkname']


# Name making functions.
def build_compound_name(names: Sequence[str],
               consonants: Sequence[str] = CONSONANTS,
               vowels: Sequence[str] = VOWELS) -> str:
    """Create a name for a character."""
    start = random.choice(names)
    end = random.choice(names)

    def get_change_index(s: str, letters):
        index = 1
        while index < len(s) and s[index] in letters:
            index += 1
        return index

    name = ''
    if end[0] not in vowels and start[0] not in vowels:
        index_start = get_change_index(start, consonants)
        index_end = get_change_index(end, consonants)
        name = start[0:index_start] + end[index_end:]
    elif end[0] in vowels and start[0] not in vowels:
        index_start = get_change_index(start, consonants)
        name = start[0:index_start] + end
    elif end[0] in vowels and start[0] in vowels:
        index_start = get_change_index(start, vowels)
        index_end = get_change_index(end, vowels)
        name = start[0:index_start] + end[index_end:]
    else:
        index_start = get_change_index(start, vowels)
        name = start[0:index_start] + end

    return name[0].upper() + name[1:]


def select_name(names: Sequence[str]) -> str:
    """Select a name from the given list."""
    return random.choice(names)
