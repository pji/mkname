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

from mkname import mkname as mn
from mkname.constants import (
    DEFAULT_DB,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_DATA,
    LOCAL_CONFIG
)
from mkname.model import Name


# Test cases.
class BuildingNamesTestCase(ut.TestCase):
    @patch('mkname.mkname.roll', side_effect=(4, 3))
    def test_build_compound_name(self, _):
        """Given a sequence of names, build_compound_name() returns a
        name constructed from the list.
        """
        # Expected value.
        exp = 'Dallory'

        # Test data and state.
        test_names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]
        names = []
        for id, test_name in enumerate(test_names):
            name = Name(id, test_name, '', '', 0, '', '')
            names.append(name)

        # Run test.
        act = mn.build_compound_name(names)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_build_from_syllables(self):
        """Given a sequence of names, return a name build from one
        syllable from each name.
        """
        # Expected value.
        exp = 'Ertalan'

        # Test data and state.
        num_syllables = 3
        test_names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]
        names = []
        for id, test_name in enumerate(test_names):
            name = Name(id, test_name, '', '', 0, '', '')
            names.append(name)
        rolls = (2, 1, 5, 2, 1, 3)
        with patch('mkname.mkname.roll') as mock_roll:
            mock_roll.side_effect = rolls

            # Run test.
            act = mn.build_from_syllables(num_syllables, names)

        # Determine test results.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll', return_value=4)
    def test_select_random_name(self, _):
        """Given a list of names, return a random name."""
        # Expected value.
        exp = 'Donatello'

        # Test data and state.
        test_names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]
        names = []
        for id, test_name in enumerate(test_names):
            name = Name(id, test_name, '', '', 0, '', '')
            names.append(name)

        # Run test.
        act = mn.select_name(names)

        # Determine test result.
        self.assertEqual(exp, act)


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

    # Tests for init_db.
    def test_init_db_with_path_and_exists(self):
        """Given the path to a database as a string, check if the
        database exists and return the path to the db."""
        # Expected value.
        exp = Path(self.test_db_loc)

        # Run test.
        act = mn.init_db(exp)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_init_db_with_str_and_exists(self):
        """Given the path to a database as a string, check if the
        database exists and return the path to the database."""
        # Expected value.
        exp = Path(self.default_db_loc)

        # Test data and state.
        location = self.default_db_loc

        # Run test.
        act = mn.init_db(location)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_init_db_with_str_and_not_exists(self):
        """Given the path to a database as a string, check if the
        database exists. If it doesn't, create the database and
        return the path to the database.
        """
        # Expected value.
        exp_file = self.default_db_loc
        exp_return = Path(self.local_db_loc)

        # Test data and state.
        act_file = self.local_db_loc

        # Run test.
        act_return = mn.init_db(act_file)

        # Determine test results.
        self.assertFileEqual(exp_file, act_file)
        self.assertEqual(exp_return, act_return)

    def test_init_db_without_path(self):
        """If no string or Path is passed, return the path to the
        default database for the package.
        """
        # Expect values.
        exp = Path(self.default_db_loc)

        # Run test.
        act = mn.init_db()

        # Determine test result.
        self.assertEqual(exp, act)

    # Tests for get_config.
    def test_get_config_default(self):
        """If no path is given and there is no local config in the
        current working directory, return the default config as a
        dict.
        """
        # Expected value.
        exp = DEFAULT_CONFIG_DATA

        # Run test.
        act = mn.get_config()

        # Determine test result.
        self.assertDictEqual(exp, act)
        self.assertFalse(exp is act)

    def test_get_config_dir(self):
        """If the passed location is a directory, raise an
        exception.
        """
        # Expected value.
        exp_ex = IsADirectoryError
        exp_msg = 'Given location is a directory.'

        # Test data and state.
        dir_ = 'tests/data/__test_mkname_test_dir'

        # Run test and determine result.
        with self.assertRaisesRegex(exp_ex, exp_msg):
            _ = mn.get_config(dir_)

    def test_get_config_fill_missing_keys(self):
        """Given the path to a config file with missing keys,
        add those keys with default values to the returned config.
        """
        # Expected value.
        exp = DEFAULT_CONFIG_DATA.copy()
        exp['db_path'] = 'spam.db'

        # Test data and state.
        location = 'tests/data/test_get_config_fill_missing_keys.cfg'

        # Run test.
        act = mn.get_config(location)

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_get_config_in_cwd(self):
        """If no path is given, check if there is a config file in
        the current working directory. If there is, return the mkname
        section from that config.
        """
        # Expected value.
        exp = self.test_full_config

        # Test data and state.
        src = self.test_config_loc
        dst = self.local_config_loc
        shutil.copy2(src, dst)

        # Run test.
        act = mn.get_config()

        # Determine test result.
        self.assertConfigEqual(exp, act)

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
