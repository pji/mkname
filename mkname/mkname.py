"""
mkname
~~~~~~

Tools for building names.
"""
import configparser
from pathlib import Path
from sqlite3 import Connection
from typing import Sequence, Union

from mkname.constants import (
    CONSONANTS,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_DATA,
    DEFAULT_DB,
    LOCAL_CONFIG,
    LOCAL_DB,
    VOWELS
)
from mkname.dice import roll
from mkname.mod import compound_names
from mkname.utility import split_into_syllables


# Initialization functions.
def get_config(location: Union[str, Path] = '') -> dict:
    """Get the configuration."""
    # Start with the default configuration.
    config_data = DEFAULT_CONFIG_DATA.copy()
    
    # Convert the passed configuration file location into a Path
    # object so we can check whether it exists. If no location was
    # passed, create a Path for a config file with a default name
    # in the current working directory in case one happens to exist
    # there.
    if location:
        path = Path(location)
    else:
        path = Path(LOCAL_CONFIG)
    
    # If the given config file doesn't exist, create a new file and
    # add the default config to it. The value of location is checked
    # here to make sure we fall back to default config if we weren't
    # passed a config file location. Otherwise, we'd spew config
    # files into every directory the script is ever run from.
    if location and not path.exists():
        defaults = DEFAULT_CONFIG_DATA.copy()
        content = [f'{key} = {defaults[key]}' for key in defaults]
        content = ['[mkname]', *content]
        with open(path, 'w') as fh:
            fh.write('\n'.join(content))

    # If the given config file now exists, get the config settings
    # from the file and overwrite the default configuration values
    # with the new values from the file.
    if path.is_file():
        config = configparser.ConfigParser()
        config.read(path)
        config_data.update(config['mkname'])
    
    # If the passed configuration file location was a directory,
    # replacing it would a valid config file could cause unexpected
    # problems. Raise an exception for the user to deal with.
    elif path.is_dir():
        msg = 'Given location is a directory.'
        raise IsADirectoryError(msg)
    
    return config_data


def init_db(path: Union[str, Path] = '') -> Path:
    """Initialize the names database."""
    # If we aren't passed the location of a database, fall back to the
    # default database for the package.
    if not path:
        path = DEFAULT_DB
    path = Path(path)
    
    # If there is nothing at the path, copy the default
    # database there.
    if not path.exists():
        with open(DEFAULT_DB, 'rb') as fh:
            contents = fh.read()
        with open(path, 'wb') as fh:
            fh.write(contents)
    
    # Return the status message.
    return path


# Name making functions.
def build_compound_name(names: Sequence[str],
               consonants: Sequence[str] = CONSONANTS,
               vowels: Sequence[str] = VOWELS) -> str:
    """Create a name for a character."""
    root_name = select_name(names)
    mod_name = select_name(names)
    return compound_names(root_name, mod_name, consonants, vowels)


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
