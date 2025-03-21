"""
.. config:

#############
Configuration
#############

Configuration of :mod:`mkname` is handled by configuration files.
Two formats are supported:

*   INI-like syntax supported by :mod:`configparser`,
*   `TOML`_ (requires Python 3.11 or higher).

.. _TOML: https://toml.io

The following describes the configuration file and how :mod:`mkname`
loads the configuration.


.. _config_files:

Configuration File Structure
============================
As mentioned above, configuration files need to be in INI-like format
or, if you are running Python 3.11 or higher, TOML format. The two
formats are very similar, so the examples will be in TOML format.
Just remember that if you use INI-like format instead, the string
values are not quoted in INI-like format.

.. note:
    Why doesn't :mod:`mkname` support TOML under Python 3.10?
    The standard library module I'm using to parse TOML,
    :mod:`tomllib` was only added to Python in 3.11. I could
    probably work around this for Python 3.10, but it seems
    like it would be more work than it's worth.

An example of the contents of a :mod:`mkname` configuration file::

    [mkname]
    consonants = "bcdfghjklmnpqrstvwxz"
    db_path =
    punctuation = "'-.?!/:@+|•"
    scifi_letters = "kqxz"
    vowels = "aeiouy"

The following is true of a :mod:`mkname` configuration file:

*   It must have a `[mkname]` section.
*   It may have any of the following keys:

    *   :ref:`consonants`,
    *   :ref:`db_path`,
    *   :ref:`punctuation`,
    *   :ref:`scifi_letters`,
    *   :ref:`vowels`.

*   No keys are required.

The keys are defined as follows.


.. _consonants:

consonants
----------
This defines the characters used as "consonants" by :mod:`mkname`. This
setting is primarily used to split names into syllables when generating
new names from multiple names from the database. The default value is
the standard list of English consonants, minus the letter `y`.


.. _db_path:

db_path
-------
This sets the names database used by :mod:`mkname`. It can be used to
have :mod:`mkname` use a custom names database rather than the default
names database. The default value is an empty string, which causes
:mod:`mkname` to go to the next step in the database search order.


.. _punctuation:

punctuation
-----------
This defines the characters used as punctuation marks by :mod:`mkname`.
This is primarily intended for use by :func:`mkname.mod.add_punctuation`
when modifying names to add punctuation marks. The default values are
listed in the example `mkname` section above.


.. _scifi_letters:

scifi_letters
-------------
The defines the characters used as "scifi letters" by :mod:`mkname`.
This is primarily intended for use by :mod:`mkname.mod.make_scifi`
when modifying names to make them seem more like names found in
pulp science fiction. The default values are listed in the example
`mkname` section above.


.. _vowels:

vowels
------
This defines the characters used as "vowels" by :mod:`mkname`. This
setting is primarily used to split names into syllables when generating
new names from multiple names from the database. The default value is
the list of English vowels, minus the letter `w`.

.. note:
    Yes, `w` is sometimes a vowel in English. It occurs in the Welsh
    loan words `cwm` and `crwth`. Why bring it up when it's only a
    few Welsh loan words and :mod:`mkname` doesn't define it as a
    vowel? Well, because it's the internet and someone would eventually
    complain if I didn't. Also, I just think it's a cool fact.


.. config_loc:

Configuration File Location
===========================
The following are the files where :mod:`mkname` looks for
configuration files.

*   In a dedicated `mkname.toml` or `mkname.cfg` file.
*   Within a `pyproject.toml` or `setup.cfg` file.

:mod:`mkname` will always look for these files in the current
working directory. If the command line tool or API call you
are using allows you to supply a configuration file path,
it will look for files of those names in that path if you
give it a path to a directory rather than a file.


.. config_load:

Loading Configuration
=====================
A configuration file doesn't need to have all keys for :mod:`mkname`
defined. To build the configuration, :mod:`mkname` will look for a
series of files, loading the configuration from each until it arrives
at the final configuration. Since the default configuration file
contains every key, this means that every key will eventually be
set regardless of whether you define it in a particular custom
config file or not.

Configuration is loaded in the following order:

*   The default configuration,
*   A `setup.cfg` file in the current working directory,
*   A `pyproject.toml` file in the current working directory (Python >= 3.11),
*   A `mkname.cfg` file in the current working directory,
*   A `mkname.toml` file in the current working directory (Python >= 3.11),
*   If a config file is explicitly passed to :mod:`mkname`, that file,
*   If a directory is explicitly passed to :mod:`mkname`, it will
    look for the following in that directory:
    *   `setup.cfg`,
    *   `pyproject.toml` (Python >= 3.11),
    *   `mkname.cfg`,
    *   `mkname.toml` (Python >= 3.11).

Since the values from the files are loaded on top of each other, files
loaded later will override values in files loaded earlier.


.. db_load:

Loading the Names Database
==========================
While :mod:`mkname` provides a :ref:`default_db`, it allows you to
create and supply your own names database. This means :mod:`mkname`
needs to have a way to decide which names database to use at runtime.


.. _db_search:

Database Search Order
---------------------
When selecting a names database to use at runtime, :mod:`mkname`
should search for a database in the following order:

1.  A file path given explicitly to :mod:`mkname`,
2.  A directory path that contains a file named `names.db` given
    explicitly to :mod:`mkname`,
3.  A path set in the :ref:`db_path` key in the configuration,
4.  A file named `names.db` in the current working directory,
5.  The default names database.

This means there are several different ways to use a customized
database when using :mod:`mkname` to generate names:

*   Place a custom names database in the current working directory.
*   Provide a configuration file that points to a custom names database.
*   Provide the path to the custom names database to :mod:`mkname`
    when generating the name. How you do this will vary depending on
    exactly what you are doing.


.. config_api:

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

    Usage:

        >>> loc = 'tests/data/test_load_config.conf'
        >>> get_config(loc)                 # doctest: +ELLIPSIS
        {'mkname': {'consonants': 'bcd', 'db_path':...

    """
    # Ensure any passed config file exists.
    path = Path(path) if path else None
    if path and not path.exists():
        msg = f'File {path} does not exist.'
        raise ConfigFileDoesNotExistError(msg)

    # Start the config with the default values.
    config = get_default_config()

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


def get_default_config() -> Config:
    """Get the default configuration values.

    :return: The default configuration as a :class:`dict`.
    :rtype: dict
    """
    default_path = get_default_path() / DEFAULTS_CONF_NAME
    return read_config(default_path)


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

    Usage::

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


# Utility functions.
def get_default_path() -> Path:
    """Get the path to the default data files.

    :return: The path to the default data location as a
        :class:`pathlib.Path`.
    :rtype: pathlib.Path
    """
    data_pkg = files(mkname.data)
    return Path(f'{data_pkg}')
