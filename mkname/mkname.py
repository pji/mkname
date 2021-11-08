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
def get_config(path: Union[str, Path] = '') -> Mapping:
    """Get the configuration."""
    if not path:
        path = LOCAL_CONFIG

    path = Path(path)
    config = configparser.ConfigParser()
    config.read(path)
    return config['mkname']


def init_db(path: Union[str, Path]) -> str:
    """Initialize the names database."""
    path = Path(path)
    msg = 'failed'
    
    # If the path is a file, return that the database exists.
    if path.is_file():
        msg = 'exists'
    
    # Otherwise, if there is nothing at the path, copy the default
    # database there.
    if not path.exists():
        with open(DEFAULT_DB, 'rb') as fh:
            contents = fh.read()
        with open(path, 'wb') as fh:
            fh.write(contents)
        msg = 'created'
    
    # Return the status message.
    return msg


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
