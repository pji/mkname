"""
init
~~~~

Basic initialization functions for :mod:`mkname`.
"""
from configparser import ConfigParser
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Union

import mkname.data


# Types.
Section = dict[str, str]
Config = dict[str, Section]


# Common data.
EXTS = ('cfg', 'conf', 'ini',)


# Configuration functions.
def get_config(path: Union[Path, str] = '') -> Config:
    """Get the configuration.

    :param location: (Optional.) The path to the configuration file.
        If no path is passed, it will default to using the default
        configuration data from mkname.constants.
    :return: A :class:`dict` object.
    :rtype: dict

    Usage:

        >>> loc = 'tests/data/test_load_config.conf'
        >>> get_config(loc)                 # doctest: +ELLIPSIS
        {'consonants': 'bcd', 'db_path':...'aei'}

    Configuration File Format
    =========================
    The file structure of the configuration file is the Windows
    INI-like structure used by Python's configparser module. The
    configuration should have two sections: `mkname` and `mkname_files`.

    mkname
    ------
    The `mkname` section can contain the following keys:

    *   `consonants`: Characters you define as consonants.
    *   `db_path`: The path to the names database.
    *   `punctuation`: Characters you define as punctuation.
    *   `scifi_letters`: A string of characters you define as being
        characteristic of science fiction names.
    *   `vowels`: Characters you define as vowels.

    mkname_files
    ------------
    The `mkname_files` section can contain the following keys:

    *   `config_file`: Name of the default configuration file.
    *   `default_db`: Name of the default database file.
    *   `local_config`: Default name when creating local configuration.
    *   `local_db`: Default name when creating a local database file.

    Example::

        [mkname]
        consonants = bcdfghjklmnpqrstvwxz
        db_path = mkname/data/names.db
        punctuation = '-
        scifi_letters: kqxz
        vowels = aeiou

        [mkname_files]
        config_file = defaults.cfg
        default_db = names.db
        local_config = mkname.cfg
        local_db = names.db
    """
    # Start the config with the default values.
    config = get_default_config()

    # If there is a local config file, override the default config
    # with the config from the local file.
    cwd = Path.cwd()
    for ext in EXTS:
        for local_path in cwd.glob(f'*.{ext}'):
            new = read_config_file(local_path)
            config.update(new)

    # If there is a given configuration file, override any found
    # config with the values from the given file.
    if path:
        given = Path(path)
        new = read_config_file(given)
        config.update(new)

    # Return the loaded configuration.
    return config


def get_default_config() -> Config:
    """Get the default configuration values."""
    default_path = get_default_path() / 'defaults.cfg'
    return read_config_file(default_path)


def get_default_path() -> Path:
    """Get the path to the default data files."""
    data_pkg = files(mkname.data)
    return Path(f'{data_pkg}')


def read_config_dir(path: Path, config: Union[dict, None] = None) -> Config:
    """Read an "INI" formatted configuration files from a directory."""
    if not config:
        config = {}
    for ext in EXTS:
        for file_path in path.glob(f'*.{ext}'):
            new = read_config_file(file_path)
            config.update(new)
    return config


def read_config_file(path: Path) -> Config:
    """Read an "INI" formatted configuration file.

    :param path: The path to the configuration file.
    :return: The contents of the configuration file as a :class:`dict`.
    :rtype: dict
    """
    # If the file doesn't exist, create it and add the default
    # config.
    if not path.exists():
        config = get_default_config()
        write_config_file(path, config)
        return config

    # If the given path was a directory, either read the config files
    # in the directory or add a new config file there.
    elif path.is_dir():
        config = read_config_dir(path)
        if not config:
            file_path = path / 'mkname.cfg'
            return read_config_file(file_path)
        return config

    # Otherwise, read in the config file and return it as a dict.
    parser = ConfigParser()
    parser.read(path)
    sections = ['mkname', 'mkname_files']
    return {k: dict(parser[k]) for k in parser if k in sections}


def write_config_file(path: Path, config: Config) -> Config:
    """Write an "INI" formatted configuration file."""
    parser = ConfigParser()
    parser.read_dict(config)
    with open(path, 'w') as fh:
        parser.write(fh)
    return config
