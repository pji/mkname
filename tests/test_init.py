"""
test_init
~~~~~~~~~

Unit tests for :mod:`mkname.init`.
"""
import configparser
import filecmp
from pathlib import Path
from sys import version_info

import pytest

import mkname.constants as c
import mkname.exceptions as mkexc
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
def given_config():
    """Pulls the default configuration values from the config file."""
    config = configparser.ConfigParser()
    config.read('tests/data/test_load_config.conf')
    keys = ['mkname', 'mkname_files']
    return {k: dict(config[k]) for k in config if k in keys}


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
    def test_get_config(self, test_conf, conf_full):
        """By default, load the configuration from the default configuration
        file stored in `mkname/mkname/data`.
        """
        assert init.get_config() == conf_full

    def test_config_in_mkname_toml(
        self, conf_full, empty_conf, mkname_toml
    ):
        """If there is configuration in the `mkname.toml` file,
        load the configuration from the `mkname.toml` file.`.
        """
        if version_info < (3, 11):
            assert init.get_config() == dict()
        else:
            assert init.get_config() == conf_full

    def test_config_in_pyproject(
        self, conf_full, empty_conf, pyproject_toml
    ):
        """If there is configuration in the `pyproject.toml` file,
        load the configuration from the `pyproject.toml` file.`.
        """
        if version_info < (3, 11):
            assert init.get_config() == dict()
        else:
            assert init.get_config() == conf_full

    def test_config_in_setup(
        self, conf_full, setup_conf
    ):
        """If there is configuration in the `setup.cfg` file, load the
        configuration from the default configuration file stored in
        `mkname/mkname/data`.
        """
        assert init.get_config() == conf_full

    def test_get_config_with_given_path(self, conf_full, test_conf_file):
        """If given a path to a configuration file,
        :func:`mkname.init.get_config` should load the
        configuration from that file.
        """
        path = Path(test_conf_file)
        assert init.get_config(path) == conf_full

    def test_get_config_with_given_dir(self, conf_full, test_conf_file):
        """If given a path to a directory with a configuration
        file, :func:`mkname.init.get_config` should load the
        configuration from that directory.
        """
        path = Path(test_conf_file).parent
        assert init.get_config(path) == conf_full

    def test_get_config_with_given_path_does_not_exist(self, tmp_path):
        """If given a path to a configuration file that
        doesn't exist', :func:`mkname.init.get_config`
        should raise a :class:`mkname.init.ConfigFileDoesNotExistError`.
        """
        path = tmp_path / 'mkname.cfg'
        with pytest.raises(init.ConfigFileDoesNotExistError):
            init.get_config(path)

    def test_get_config_with_given_str(self, given_config):
        """If given a str with the path to a configuration file,
        :func:`mkname.init.get_config` should load the configuration
        from that file.
        """
        path = 'tests/data/test_load_config.conf'
        assert init.get_config(path) == given_config

    def test_get_config_with_local(self, mkname_cfg, conf_full):
        """If there is a configuration file in the current working directory,
        :func:`mkname.init.get_config` should load the configuration from
        that file.
        """
        assert init.get_config() == conf_full

    def test_get_config_with_partial_local(
        self, mkname_cfg_partial, conf_partial
    ):
        """If there is a configuration file in the current working directory,
        :func:`mkname.init.get_config` should load the configuration from
        that file. If the config doesn't have values for all possible keys,
        the missing keys should have the default values.
        """
        assert init.get_config() == conf_partial


# Test init_db.
class TestGetDB:
    def test_default(self):
        """By default, :func:`mkname.init.get_db` should return the path to
        the default database.
        """
#         assert init.get_db() == Path(c.DEFAULT_DB)
        assert init.get_db() == Path('src/mkname/data/names.db').absolute()

    def test_db_in_cwd(self, run_in_tmp_with_db):
        """When not given a path and there is a names database
        in the current working directory, :fun:`mkname.init.get_db`
        should return the path to the names database in the current
        working directory.
        """
        assert init.get_db() == Path(run_in_tmp_with_db)

    def test_db_in_config(self, db_path, test_conf):
        """When not given a path and there is a names database
        defined in the config, :fun:`mkname.init.get_db`
        should return the path to the names database in the config.
        """
        assert not Path('./names.db').exists()
        path = Path(db_path)
        result = init.get_db()
        assert result == path

    def test_db_given_config(self, db_path, conf_full_path):
        """When not given a path and there is a names database
        defined in the given config, :fun:`mkname.init.get_db`
        should return the path to the names database in the config.
        """
        assert not Path('./names.db').exists()
        path = Path(db_path)
        result = init.get_db(conf_path=conf_full_path)
        assert result == path

    def test_path_exists(self, db_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db.
        """
        test_db_loc = Path(db_path)
        assert init.get_db(test_db_loc) == test_db_loc

    def test_path_is_directory_and_db_exists(self, db_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db. If the path is a directory
        containing a file named `names.db`, it should return the path
        to that file.
        """
        test_db_loc = Path(db_path)
        test_dir_loc = test_db_loc.parent
        assert init.get_db(test_dir_loc) == test_db_loc

    def test_path_does_not_exists(self, test_db, tmp_path):
        """Given the path to a database as a :class:`pathlib.Path`,
        :func:`mkname.init.get_db` should check if the database exists
        and return the path to the db. If the database doesn't exist,
        raise a NotADatabaseError.
        """
        db_path = tmp_path / 'names.db'
        assert not db_path.exists()
        with pytest.raises(mkexc.NotADatabaseError):
            init.get_db(db_path) == db_path

    def test_str_exists(self, db_path):
        """Given the path to a database as a :class:`str`,
        :func:`mkname.init.get_db` should check if the
        database exists and return the path to the db.
        """
        db_path = str(db_path)
        assert init.get_db(db_path) == Path(db_path)
