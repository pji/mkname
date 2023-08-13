"""
test_mkname
~~~~~~~~~~~
"""
import filecmp
from pathlib import Path
import shutil
import unittest as ut
from unittest.mock import patch
from typing import Mapping

import pytest

from mkname import mkname as mn
from mkname.constants import (
    DEFAULT_DB,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_DATA,
    LOCAL_CONFIG
)
from mkname.model import Name


# Fixtures.
@pytest.fixture
def local_config_loc():
    loc = Path(LOCAL_CONFIG)
    yield loc
    if loc.exists():
        loc.unlink()


@pytest.fixture
def local_db_loc():
    loc = Path('test_names.db')
    yield loc
    if loc.exists():
        loc.unlink()


@pytest.fixture
def names():
    return [Name(id, name, '', '', 0, '', '') for id, name in enumerate([
        'Alice',
        'Robert',
        'Mallory',
        'Donatello',
        'Michealangelo',
        'Leonardo',
        'Raphael',
    ])]


@pytest.fixture
def test_config():
    return {
        'consonants': 'bcd',
        'db_path': 'spam.db',
        'punctuation': "'-",
        'scifi_letters': 'eggs',
        'vowels': 'aei'
    }


# Building names test cases.
def test_build_compound_name(names, mocker):
    """Given a sequence of names, build_compound_name() returns a
    name constructed from the list.
    """
    mocker.patch('yadr.roll', side_effect=[4, 3])
    assert mn.build_compound_name(names) == 'Dallory'


def test_build_from_syllables(names, mocker):
    """Given a sequence of names, return a name build from one
    syllable from each name.
    """
    mocker.patch('yadr.roll', side_effect=[2, 1, 5, 2, 1, 3])
    num_syllables = 3
    assert mn.build_from_syllables(num_syllables, names) == 'Ertalan'


def test_select_random_name(names, mocker):
    """Given a list of names, return a random name."""
    mocker.patch('yadr.roll', side_effect=[4,])
    assert mn.select_name(names) == 'Donatello'


# Initialization test cases.
# Tests for init_db.
def test_init_db_with_path_and_exists():
    """Given the path to a database as a string, check if the
    database exists and return the path to the db.
    """
    test_db_loc = Path('tests/data/names.db')
    assert mn.init_db(test_db_loc) == test_db_loc


def test_init_db_with_str_and_exists():
    """Given the path to a database as a string, check if the
    database exists and return the path to the database.
    """
    assert mn.init_db(DEFAULT_DB) == Path(DEFAULT_DB)


def test_init_db_with_str_and_not_exists(local_db_loc):
    """Given the path to a database as a string, check if the
    database exists. If it doesn't, create the database and
    return the path to the database.
    """
    assert mn.init_db(local_db_loc) == local_db_loc
    assert filecmp.cmp(Path(DEFAULT_DB), local_db_loc, shallow=False)


def test_init_db_without_path():
    """If no string or Path is passed, return the path to the
    default database for the package.
    """
    assert mn.init_db() == Path(DEFAULT_DB)


# Tests for get_config.
def test_get_config_default():
    """If no path is given and there is no local config in the
    current working directory, return the default config as a
    dict.
    """
    result = mn.get_config()
    assert result == DEFAULT_CONFIG_DATA
    assert result is not DEFAULT_CONFIG_DATA


def test_get_config_dir():
    """If the passed location is a directory, raise an
    exception.
    """
    ex = IsADirectoryError
    msg = 'Given location is a directory.'
    loc = 'tests/data/__test_mkname_test_dir'
    with pytest.raises(ex, match=msg):
        mn.get_config(loc)


def test_get_config_fill_missing_keys():
    """Given the path to a config file with missing keys,
    add those keys with default values to the returned config.
    """
    # Expected value.
    expected = DEFAULT_CONFIG_DATA.copy()
    expected['db_path'] = 'spam.db'

    # Test data and state.
    location = 'tests/data/test_get_config_fill_missing_keys.cfg'

    # Run test and determine result.
    assert mn.get_config(location) == expected


def test_get_config_in_cwd(local_config_loc, test_config):
    """If no path is given, check if there is a config file in
    the current working directory. If there is, return the mkname
    section from that config.
    """
    test_config_loc = 'tests/data/test_load_config.conf'
    shutil.copy2(test_config_loc, local_config_loc)
    assert mn.get_config() == test_config


class InitializationTestCase(ut.TestCase):
    default_config_loc = DEFAULT_CONFIG
    default_db_loc = DEFAULT_DB
    local_config_loc = LOCAL_CONFIG
    local_db_loc = 'test_names.db'
    test_config_loc = 'tests/data/test_load_config.conf'
    test_db_loc = 'tests/data/names.db'
    test_dir_loc = 'tests/data/__test_mkname_test_dir'
    test_full_config = {
        'consonants': 'bcd',
        'db_path': 'spam.db',
        'punctuation': "'-",
        'scifi_letters': 'eggs',
        'vowels': 'aei'
    }

    def assertConfigEqual(self, a: Mapping, b: Mapping) -> None:
        """Assert that two ParserConfig objects are equal."""
        a_keylist = list(a.keys())
        b_keylist = list(b.keys())
        self.assertListEqual(a_keylist, b_keylist)
        for key in a:
            if isinstance(a[key], Mapping):
                self.assertConfigEqual(a[key], b[key])
            else:
                self.assertEqual(a[key], b[key])

    def assertFileEqual(self, a, b):
        """Compare the files as two paths."""
        a_path = Path(a)
        b_path = Path(b)
        for path in a_path, b_path:
            if not path.is_file():
                msg = f'{path} is not a file.'
                raise RuntimeError(msg)

        self.assertTrue(filecmp.cmp(a, b, shallow=False))

    def get_common_paths(self):
        return (
            Path(self.local_config_loc),
            Path(self.local_db_loc),
        )

    def setUp(self):
        paths = self.get_common_paths()
        msg = '{} exists. Aborting test.'
        for path in paths:
            if path.exists():
                raise FileExistsError(msg.format(path))

    def tearDown(self):
        paths = self.get_common_paths()
        for path in paths:
            if path.exists():
                path.unlink()

    # Tests for get_config.
    def test_get_config_with_path(self):
        """Given the path to a configuration file as a string,
        return the mkname configuration found in that file.
        """
        # Expected value.
        exp = self.test_full_config

        # Test data and state.
        path_str = self.test_config_loc
        path = Path(path_str)

        # Run test.
        act = mn.get_config(path)

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_get_config_with_str(self):
        """Given the path to a configuration file as a string,
        return the mkname configuration found in that file.
        """
        # Expected value.
        exp = self.test_full_config

        # Test data and state.
        path_str = self.test_config_loc

        # Run test.
        act = mn.get_config(path_str)

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_get_config_with_str_and_not_exists(self):
        """Given the path to a configuration file as a string,
        check if the file exists. If not, copy the default config
        to that location, then return the mkname configuration found
        in that file.
        """
        # Expected value.
        exp_config = DEFAULT_CONFIG_DATA
        exp_file = Path(self.local_config_loc)

        # Test data and state.
        path = self.local_config_loc

        # Run test.
        act_config = mn.get_config(path)

        # Determine test result.
        self.assertConfigEqual(exp_config, act_config)
        self.assertTrue(exp_file.is_file())
