"""
test_init
~~~~~~~~~

Unit tests for :mod:`mkname.init`.
"""
import configparser
import filecmp
from pathlib import Path

import pytest

from mkname import init
import mkname.constants as c


# Fixtures.
@pytest.fixture
def config_directory():
    path = Path('_test_config_directory')
    path.mkdir()
    link = path / 'spam.cfg'
    config_path = Path('tests/data/test_load_config.conf')
    link.hardlink_to(config_path)
    yield path
    link.unlink()
    for child in path.iterdir():
        child.unlink()
    path.rmdir()


@pytest.fixture
def default_config():
    """Pulls the default configuration values from the config file."""
    config = configparser.ConfigParser()
    config.read(c.DEFAULT_CONFIG)
    keys = ['mkname', 'mkname_files']
    return {k: dict(config[k]) for k in config if k in keys}


@pytest.fixture
def given_config():
    """Pulls the default configuration values from the config file."""
    config = configparser.ConfigParser()
    config.read('tests/data/test_load_config.conf')
    keys = ['mkname', 'mkname_files']
    return {k: dict(config[k]) for k in config if k in keys}


@pytest.fixture
def local_config():
    """Moves a config file into the current working directory,
    yields the contents of that config, then cleans up.
    """
    # Create the test config in the CWD.
    path = Path('tests/data/test_load_config.conf')
    link = Path('mkname.cfg')
    link.hardlink_to(path)

    # Send the contents of the config to the test.
    config = configparser.ConfigParser()
    config.read(link)
    keys = ['mkname', 'mkname_files']
    yield {k: dict(config[k]) for k in config if k in keys}

    # Clean up after test.
    if link.exists():
        link.unlink()


@pytest.fixture
def local_db_loc():
    loc = Path('test_names.db')
    yield loc
    if loc.exists():
        loc.unlink()


@pytest.fixture
def partial_local_config():
    """Moves a partial config file into the current working directory,
    yields the contents of that config, then cleans up.
    """
    # Create the test config in the CWD.
    path = Path('tests/data/test_use_config.cfg')
    link = Path('mkname.conf')
    link.hardlink_to(path)

    # Send the contents of the config to the test.
    config = configparser.ConfigParser()
    config.read(link)
    keys = ['mkname', 'mkname_files']
    yield {k: dict(config[k]) for k in config if k in keys}

    # Clean up after test.
    if link.exists():
        link.unlink()


@pytest.fixture
def not_exist_config():
    path = Path('_test_given_path_does_not_exist.ini')
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture
def empty_directory():
    path = Path('_test_empty_directory')
    path.mkdir()
    yield path
    for child in path.iterdir():
        child.unlink()
    if path.exists():
        path.rmdir()


# Test get_config.
def test_get_config(default_config):
    """By default, load the configuration from the default configuration
    file stored in `mkname/mkname/data`.
    """
    assert init.get_config() == default_config


def test_get_config_with_given_path(given_config):
    """If given a path to a configuration file,
    :func:`mkname.init.get_config` should load the
    configuration from that file.
    """
    path = Path('tests/data/test_load_config.conf')
    assert init.get_config(path) == given_config


def test_get_config_with_given_path_does_not_exist(
    default_config, not_exist_config
):
    """If given a path to a configuration file,
    :func:`mkname.init.get_config` should load the
    configuration from that file. If that file does
    not exist, that file should be created and
    populated with the default config.
    """
    assert not not_exist_config.exists()
    assert init.get_config(not_exist_config) == default_config
    assert not_exist_config.exists()
    assert init.get_config(not_exist_config) == default_config


def test_get_config_with_given_path_is_config_directory(
    given_config, config_directory
):
    """If given a path to a directory with a configuration file,
    :func:`mkname.init.get_config` should read the configuration
    from the configuration file.
    """
    assert init.get_config(config_directory) == given_config


def test_get_config_with_given_path_is_empty_directory(
    default_config, empty_directory
):
    """If given a path to a directory without a configuration file,
    :func:`mkname.init.get_config` should create a file with the
    default local configuration file name in that directory with
    the default configuration values.
    """
    assert not [_ for _ in empty_directory.iterdir()]
    assert init.get_config(empty_directory) == default_config

    path = empty_directory / 'mkname.cfg'
    assert path.exists()
    assert init.get_config(path) == default_config


def test_get_config_with_given_str(given_config):
    """If given a str with the path to a configuration file,
    :func:`mkname.init.get_config` should load the configuration
    from that file.
    """
    path = 'tests/data/test_load_config.conf'
    assert init.get_config(path) == given_config


def test_get_config_with_local(local_config):
    """If there is a configuration file in the current working directory,
    :func:`mkname.init.get_config` should load the configuration from
    that file.
    """
    assert init.get_config() == local_config


def test_get_config_with_partial_local(partial_local_config, default_config):
    """If there is a configuration file in the current working directory,
    :func:`mkname.init.get_config` should load the configuration from
    that file. If the config doesn't have values for all possible keys,
    the missing keys should have the default values.
    """
    config = default_config
    config.update(partial_local_config)
    assert init.get_config() == config


# Test init_db.
def test_get_db():
    """By default, :func:`mkname.init.get_db` should return the path to
    the default database.
    """
    assert init.get_db() == Path(c.DEFAULT_DB)


def test_get_db_with_path_and_exists():
    """Given the path to a database as a :class:`pathlib.Path`,
    :func:`mkname.init.get_db` should check if the database exists
    and return the path to the db.
    """
    test_db_loc = Path('tests/data/names.db')
    assert init.get_db(test_db_loc) == test_db_loc


def test_get_db_with_path_is_directory_and_db_exists():
    """Given the path to a database as a :class:`pathlib.Path`,
    :func:`mkname.init.get_db` should check if the database exists
    and return the path to the db. If the path is a directory
    containing a file named `names.db`, it should return the path
    to that file.
    """
    test_dir_loc = Path('tests/data')
    test_db_loc = Path('tests/data/names.db')
    assert init.get_db(test_dir_loc) == test_db_loc


def test_init_db_with_path_and_not_exists(local_db_loc):
    """Given the path to a database as a :class:`pathlib.Path`,
    :func:`mkname.init.get_db` should check if the database exists
    and return the path to the db. If the database doesn't exist,
    the database should be created with default data, and the path
    to the new database returned.
    """
    assert init.get_db(local_db_loc) == local_db_loc
    assert filecmp.cmp(Path(c.DEFAULT_DB), local_db_loc, shallow=False)


def test_get_db_with_str_and_exists():
    """Given the path to a database as a :class:`str`,
    :func:`mkname.init.get_db` should check if the
    database exists and return the path to the db.
    """
    test_db_loc = 'tests/data/names.db'
    assert init.get_db(test_db_loc) == Path(test_db_loc)
