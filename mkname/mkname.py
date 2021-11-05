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
    return config['DEFAULT']


# Name making functions.
def build_compound_name(names: Sequence[str],
               consonants: Sequence[str] = CONSONANTS,
               vowels: Sequence[str] = VOWELS) -> str:
    """Create a name for a character."""
    start = random.choice(names)
    end = random.choice(names)
    return compound_names(start, end, consonants, vowels)


def build_from_syllables(num_syllables: int,
                         names: Sequence[str],
                         consonants: Sequence[str] = CONSONANTS,
                         vowels: Sequence[str] = VOWELS) -> str:
    """Build a name from the syllables of the given names."""
    base_names = [select_name(names) for _ in range(num_syllables)]
    
    result = ''
    for name in base_names:
        syllables = split_into_syllables(name)
        index = roll(f'1d{len(syllables)}') - 1
        syllable = syllables[index]
        result = f'{result}{syllable}'
    return result.title()


def select_name(names: Sequence[str]) -> str:
    """Select a name from the given list."""
    index = roll(f'1d{len(names)}') - 1
    return names[index]
