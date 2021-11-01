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
from mkname.mod import compound_names
from mkname.utility import split_into_syllables


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
    return compound_names(start, end, consonants, vowels)


def build_from_syllables(names: Sequence[str],
                         consonants: Sequence[str] = CONSONANTS,
                         vowels: Sequence[str] = VOWELS) -> str:
    """Build a name from the syllables of the given names."""
    result = ''
    for name in names:
        syllables = split_into_syllables(name)
        index = roll(f'1d{len(syllables)}') - 1
        syllable = syllables[index]
        result = f'{result}{syllable}'
    return result


def select_name(names: Sequence[str]) -> str:
    """Select a name from the given list."""
    return random.choice(names)
