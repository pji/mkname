"""
test_init
~~~~~~~~~

Unit tests for :mod:`mkname.init`.
"""
import configparser
import filecmp
from pathlib import Path

import pytest

import mkname.constants as c
from mkname import init
from tests.fixtures import *


# Fixtures.
@pytest.fixture
def config_directory(conf_full_path, tmp_path):
    """A path to a directory with a config file."""
    text = conf_full_path.read_text()
    path = tmp_path / 'spam.cfg'
    path.write_text(text)
    yield tmp_path


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
def local_config(conf_full_path, run_in_tmp):
    """Moves a config file into the current working directory,
    yields the contents of that config, then cleans up.
    """
    # Create the test config in the CWD.
    text = Path(conf_full_path).read_text()
    temp_conf = run_in_tmp / 'mkname.conf'
    temp_conf.write_text(text)

    # Send the contents of the config to the test.
    config = configparser.ConfigParser()
    config.read(temp_conf)
    keys = ['mkname', 'mkname_files']
    yield {k: dict(config[k]) for k in config if k in keys}


@pytest.fixture
def partial_local_config(conf_path, run_in_tmp):
    """Moves a partial config file into the current working directory,
    yields the contents of that config, then cleans up.
    """
    # Create the test config in the CWD.
    text = Path(conf_path).read_text()
    temp_conf = run_in_tmp / 'mkname.conf'
    temp_conf.write_text(text)

    # Send the contents of the config to the test.
    config = configparser.ConfigParser()
    config.read(temp_conf)
    keys = ['mkname', 'mkname_files']
    yield {k: dict(config[k]) for k in config if k in keys}


# Test cases.
class TestGetConfig:
    def test_get_config(self, default_config):
        """By default, load the configuration from the default configuration
        file stored in `mkname/mkname/data`.
        """
        assert init.get_config() == default_config

    def test_get_config_with_given_path(self, given_config):
        """If given a path to a configuration file,
        :func:`mkname.init.get_config` should load the
        configuration from that file.
        """
        path = Path('tests/data/test_load_config.conf')
        assert init.get_config(path) == given_config

    def test_get_config_with_given_path_does_not_exist(
        self, default_config, tmp_path
    ):
        """If given a path to a configuration file,
        :func:`mkname.init.get_config` should load the
        configuration from that file. If that file does
        not exist, that file should be created and
        populated with the default config.
        """
        path = tmp_path / 'mkname.ini'
        assert not path.exists()
        assert init.get_config(path) == default_config
        assert path.exists()
        assert init.get_config(path) == default_config

    def test_get_config_with_given_path_is_config_directory(
        self, given_config, config_directory
    ):
        """If given a path to a directory with a configuration file,
        :func:`mkname.init.get_config` should read the configuration
        from the configuration file.
        """
        assert init.get_config(config_directory) == given_config

    def test_get_config_with_given_path_is_empty_directory(
        self, default_config, tmp_path
    ):
        """If given a path to a directory without a configuration file,
        :func:`mkname.init.get_config` should create a file with the
        default local configuration file name in that directory with
        the default configuration values.
        """
        assert init.get_config(tmp_path) == default_config

        path = tmp_path / 'mkname.cfg'
        assert path.exists()
        assert init.get_config(path) == default_config

    def test_get_config_with_given_str(self, given_config):
        """If given a str with the path to a configuration file,
        :func:`mkname.init.get_config` should load the configuration
        from that file.
        """
        path = 'tests/data/test_load_config.conf'
        assert init.get_config(path) == given_config

    def test_get_config_with_local(self, local_config):
        """If there is a configuration file in the current working directory,
        :func:`mkname.init.get_config` should load the configuration from
        that file.
        """
        assert init.get_config() == local_config

    def test_get_config_with_partial_local(
        self, partial_local_config, default_config
    ):
        """If there is a configuration file in the current working directory,
        :func:`mkname.init.get_config` should load the configuration from
        that file. If the config doesn't have values for all possible keys,
        the missing keys should have the default values.
        """
        config = default_config
        config.update(partial_local_config)
        assert init.get_config() == config


# Test init_db.
class TestGetDB:
    def test_get_db(self):
        """By default, :func:`mkname.init.get_db` should return the path to
        the default database.
        """
        assert init.get_db() == Path(c.DEFAULT_DB)

    def test_get_db_with_path_and_exists(self, db_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db.
        """
        test_db_loc = Path(db_path)
        assert init.get_db(test_db_loc) == test_db_loc

    def test_get_db_with_path_is_directory_and_db_exists(self, db_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db. If the path is a directory
        containing a file named `names.db`, it should return the path
        to that file.
        """
        test_db_loc = Path(db_path)
        test_dir_loc = test_db_loc.parent
        assert init.get_db(test_dir_loc) == test_db_loc

    def test_init_db_with_path_and_not_exists(self, test_db, tmp_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db. If the database doesn't exist,
        the database should be created with default data, and the path
        to the new database returned.
        """
        db_path = tmp_path / 'names.db'
        assert not db_path.exists()
        assert init.get_db(db_path) == db_path
        assert filecmp.cmp(Path(test_db), db_path, shallow=False)

    def test_get_db_with_str_and_exists(self, db_path):
        """Given the path to a database as a :class:`str`,
        :func:`mkname.init.get_db` should check if the
        database exists and return the path to the db.
        """
        db_path = str(db_path)
        assert init.get_db(db_path) == Path(db_path)
