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
    """Get the default configuration values.

    :return: The default configuration as a :class:`dict`.
    :rtype: dict
    """
    default_path = get_default_path() / 'defaults.cfg'
    return read_config_file(default_path)


def read_config_dir(path: Path, config: Union[dict, None] = None) -> Config:
    """Read an "INI" formatted configuration files from a directory.

    :param path: The path to the configuration directory.
    :config: Default configuration values.
    :return: The loaded configuration as a :class:`dict`.
    :rtype: dict
    """
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
    """Write an "INI" formatted configuration file.

    :param path: The path to the configuration file to write.
    :param config: The values to write into the configuration file.
    :return: The configuration values written into the files.
    :rtype: dict
    """
    parser = ConfigParser()
    parser.read_dict(config)
    with open(path, 'w') as fh:
        parser.write(fh)
    return config


# Database functions.
def get_db(path: Union[Path, str] = '') -> Path:
    """Get the path to the names database.

    :param path: The path of the names database.
    :return: The path to the names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path

    Usage::

        >>> loc = 'mkname/data/names.db'
        >>> init_db(loc)
        PosixPath('mkname/data/names.db')

    Database Structure
    ------------------
    The names database is a sqlite3 database with a table named
    'names'. The names table has the following columns:

    *   `id`: A unique identifier for the name.
    *   `name`: The name.
    *   `source`: The URL where the name was found.
    *   `culture`: The culture or nation the name is tied to.
    *   `date`: The approximate year the name is tied to.
    *   `kind`: A tag for how the name is used, such as a given
        name or a surname.
    """
    # By default use the default database.
    if not path:
        path = get_default_db()
    path = Path(path)

    # If the database doesn't exist, create it.
    if not path.exists():
        path = write_db_file(path)

    # If the path is a directory, return the database in the directory.
    if path.is_dir():
        path = get_db_dir(path)

    # Return the path to the database.
    return path


def get_db_dir(path: Path) -> Path:
    """Get the database file from the given directory. If it doesn't
    exist in the directory, create it.

    :param path: The path of the directory.
    :return: The path to the names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    path = path / 'names.db'
    return get_db(path)


def get_default_db() -> Path:
    """Get the path to the default names database.

    :return: The path to the default names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    return get_default_path() / 'names.db'


def write_db_file(path: Path) -> Path:
    """Write the default named database to the given path.

    :param path: The path for the new names database.
    :return: The path to the new names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    default_path = get_default_db()
    with open(default_path, 'rb') as fh:
        contents = fh.read()
    with open(path, 'wb') as fh:
        fh.write(contents)
    return path


# Utility functions.
def get_default_path() -> Path:
    """Get the path to the default data files.

    :return: The path to the default data location as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    data_pkg = files(mkname.data)
    return Path(f'{data_pkg}')
