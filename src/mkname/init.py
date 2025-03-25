"""
.. _config_api:

Configuration API
=================

The following are the basic initialization functions for :mod:`mkname`.

.. autofunction:: mkname.get_config
.. autofunction:: mkname.get_db

"""
from configparser import ConfigParser
from importlib.resources import files
from pathlib import Path
from sys import version_info
from typing import Union


if version_info >= (3, 11):
    import tomllib

import mkname.data
from mkname.exceptions import *
from mkname.model import Config, Section


# Common data.
DB_NAME = 'names.db'
DEFAULTS_CONF_NAME = 'defaults.cfg'
CONF_NAMES = (
    ('setup.cfg', (3, 10)),
    ('pyproject.toml', (3, 11)),
    ('mkname.cfg', (3, 10)),
    ('mkname.toml', (3, 11)),
)


# Configuration functions.
def build_search_paths(path: Path | None) -> list[Path]:
    """Build the list of paths where config files might be.

    :param path: Any path given by the user for a config file.
    :returns: A :class:`list` object.
    :rtype: list
    """
    # The core configuration files.
    search_paths = [
        Path.cwd() / filename for filename, version in CONF_NAMES
        if version_info >= version
    ]
    search_paths = [get_default_config(), *search_paths]

    # If the given path is a file, add that file to the search paths.
    if path and path.is_file():
        search_paths.append(path)

    # If the given path is a directory, search for each of the
    # filenames for the core configuration files in that directory.
    elif path and path.is_dir():
        search_paths.extend(
            path / filename for filename, version in CONF_NAMES
            if version_info >= version
        )

    # Return the search paths.
    return search_paths


def get_config(path: Path | str | None = None) -> Config:
    """Get the configuration.

    :param location: (Optional.) The path to the configuration file.
        If no path is passed or the passed path doesn't exist, it will
        fall back to a series of other files. See "Loading Configuration".
    :return: A :class:`dict` object.
    :rtype: dict

    :usage:

    .. doctest:: config

        >>> loc = 'tests/data/test_load_config.conf'
        >>> get_config(loc)
        {'mkname': {'consonants': 'bcd', 'db_path':...

    """
    # Ensure any passed config file exists.
    path = Path(path) if path else None
    if path and not path.exists():
        msg = f'File {path} does not exist.'
        raise ConfigFileDoesNotExistError(msg)

    # Start the config with the default values.
    config: Config = dict()

    # Search through possible config files and update the config.
    search_paths = build_search_paths(path)
    for search_path in search_paths:
        if search_path and search_path.exists():
            if search_path.suffix == '.toml':
                new = read_toml(search_path)
            else:
                new = read_config(search_path)
            for key in new:
                config.setdefault(key, dict())
                config[key].update(new[key])

    # Return the loaded configuration.
    return config


def get_default_config() -> Path:
    """Get the default configuration values.

    :return: The default configuration as a :class:`dict`.
    :rtype: dict
    """
    default_path = get_default_path() / DEFAULTS_CONF_NAME
    return default_path


def read_config(path: Path) -> Config:
    """Read the configuration file at the given path.

    :param path: The path to the configuration file.
    :return: The configuration as a :class:`dict`.
    :rtype: dict
    """
    parser = ConfigParser()
    parser.read(path)
    sections = ['mkname', 'mkname_files']
    return {k: dict(parser[k]) for k in parser if k in sections}


def read_toml(path: Path) -> Config:
    """Read the TOML file at the given path.

    :param path: The path to the TOML file.
    :return: The configuration as a :class:`dict`.
    :rtype: dict
    """
    if version_info < (3, 11):
        msg = f'Python {version_info} does not support TOML.'
        raise UnsupportedPythonVersionError(msg)
    with open(path, 'rb') as fh:
        data = tomllib.load(fh)
    sections = ['mkname', 'mkname_files']
    return {k: dict(data[k]) for k in data if k in sections}


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
def get_db(
    path: Path | str | None = None,
    conf_path: Path | str | None = None
) -> Path:
    """Get the path to the names database.

    :param path: The path of the names database.
    :return: The path to the names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path

    :usage:

    .. doctest:: config

        >>> loc = 'src/mkname/data/names.db'
        >>> get_db(loc)
        PosixPath('src/mkname/data/names.db')

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
    # Get the config.
    config = get_config(conf_path)
    cfg_path = config['mkname']['db_path']

    # The search paths.
    explicit_path = Path(path) if path else None
    config_path = Path(cfg_path) if cfg_path else None
    local_path = Path.cwd() / DB_NAME
    default_path = get_default_db()

    # If we are passed an explicit database path, use that database.
    if explicit_path:
        if explicit_path.is_dir():
            explicit_path = explicit_path / DB_NAME
        db_path = explicit_path

    # If there is no explicit database given, check if one was
    # configured.
    elif config_path:
        db_path = config_path

    # If we weren't given a database, check if there is one in
    # the current working directory.
    elif local_path.is_file():
        db_path = local_path

    # If all alse fails, use the default database.
    else:
        db_path = default_path

    # Double check to make sure the path could be a database.
    # Yelp if it isn't.
    if not db_path.is_file():
        msg = f'{path} is not a file.'
        if db_path == default_path:
            msg = f'The default database is missing. Reinstall mkname.'
        raise NotADatabaseError(msg)

    # Return the path to the database.
    return db_path


def get_default_db() -> Path:
    """Get the path to the default names database.

    :return: The path to the default names database as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    return get_default_path() / DB_NAME


# Text functions.
def get_text(path: Path | str) -> str:
    """Get text from a text file in the package data.

    :param path: The relative path to the text file within the
        package data.
    :returns: A :class:`str` object.
    :rtype: str
    """
    pkg_data = get_default_path()
    path = pkg_data / path
    return path.read_text()


# Utility functions.
def get_default_path() -> Path:
    """Get the path to the default data files.

    :return: The path to the default data location as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    data_pkg = files(mkname.data)
    return Path(f'{data_pkg}')
