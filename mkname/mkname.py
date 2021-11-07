"""
mkname
~~~~~~

Tools for building names.
"""
import configparser
from pathlib import Path
import random
from typing import Mapping, Sequence, Union

from mkname.constants import (
    CONSONANTS,
    DEFAULT_CONFIG,
    DEFAULT_DB,
    LOCAL_CONFIG,
    LOCAL_DB,
    VOWELS
)
from mkname.dice import roll
from mkname.mod import compound_names
from mkname.utility import split_into_syllables


# Initialization functions.
def init_config(filepath: Union[str, Path] = '') -> str:
    """Initialize a config file on the first run of the module."""
    if not filepath:
        filepath = LOCAL_CONFIG
    p = Path(filepath)
    
    # If the local configuration file doesn't exist, create it.
    if not p.is_file():
        with open(DEFAULT_CONFIG) as fh:
            contents = fh.read()
        with open(LOCAL_CONFIG, 'w') as fh:
            fh.write(contents)
        return 'created'
    
    # Otherwise, just return that the config existed.
    return 'exists'


def init_db() -> str:
    """Initialize a names database on the first run of the module."""
    p = Path(LOCAL_DB)
    
    # If the local names database doesn't exist, create it.
    if not p.is_file():
        with open(DEFAULT_DB, 'rb') as fh:
            contents = fh.read()
        with open(LOCAL_DB, 'wb') as fh:
            fh.write(contents)
        return 'created'
    
    # Otherwise, just return that the database existed.
    return 'exists'


def load_config(filepath: Union[str, Path]) -> Mapping:
    """Load the configuration."""
    # If the config doesn't exist in the given location, initialize it.
    _ = init_config(filepath)
    
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
