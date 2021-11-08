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
from mkname import dice as r
from mkname.constants import DEFAULT_DB, LOCAL_CONFIG, LOCAL_DB


# Test cases.
class BuildingNamesTestCase(ut.TestCase):
    def test_build_compound_name(self):
        """Given a sequence of names, build_compound_name() returns a
        name constructed from the list.
        """
        # Expected value.
        exp = 'Dallory'

        # Test data and state.
        r._seed('spam12')
        names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]

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
        names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]
        rolls = (2, 1, 5, 2, 1, 3)
        with patch('mkname.mkname.roll') as mock_roll:
            mock_roll.side_effect = rolls

            # Run test.
            act = mn.build_from_syllables(num_syllables, names)

        # Determine test results.
        self.assertEqual(exp, act)

    def test_select_random_name(self):
        """Given a list of names, return a random name."""
        # Expected value.
        exp = 'Donatello'

        # Test data and state.
        r._seed('spam12')
        names = [
            'Alice',
            'Robert',
            'Mallory',
            'Donatello',
            'Michealangelo',
            'Leonardo',
            'Raphael',
        ]

        # Run test.
        act = mn.select_name(names)

        # Determine test result.
        self.assertEqual(exp, act)


class InitializationTestCase(ut.TestCase):
    default_db_loc = DEFAULT_DB
    local_config_loc = LOCAL_CONFIG
    local_db_loc = 'test_names.db'
    test_config_loc = 'tests/data/test_load_config.conf'
    test_db_loc = 'tests/data/names.db'

    def assertConfigEqual(self, a: Mapping, b: Mapping) -> None:
        """Assert that two ParserConfig objects are equal."""
        a_keylist = list(a.keys())
        b_keylist = list(b.keys())
        self.assertListEqual(a_keylist, b_keylist)
        for key in a:
            if not isinstance(a[key], str):
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
                raise RuntimeError(msg.format(path))

    def tearDown(self):
        paths = self.get_common_paths()
        for path in paths:
            if path.exists():
                path.unlink()

    # Tests for init_db.
    def test_init_db_with_location_as_str_and_exists(self):
        """Given the path to a database as a string, check if the
        database exists. If it does, return 'exists'."""
        # Expected value.
        exp = 'exists'

        # Test data and state.
        location = 'tests/data/names.db'

        # Run test.
        act = mn.init_db(location)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_init_db_with_location_as_path_and_exists(self):
        """Given the path to a database as a string, check if the
        database exists. If it does, return 'exists'."""
        # Expected value.
        exp = 'exists'

        # Test data and state.
        location = self.test_db_loc
        path = Path(location)

        # Run test.
        act = mn.init_db(path)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_init_db_with_location_as_str_and_not_eists(self):
        """Given the path to a database as a string, check if the
        database exists. If it doesn't, create the database and
        return 'created'.
        """
        # Expected value.
        exp_file = self.default_db_loc
        exp_return = 'created'

        # Test data and state.
        act_file = self.local_db_loc

        # Run test.
        act_return = mn.init_db(act_file)

        # Determine test results.
        self.assertFileEqual(exp_file, act_file)
        self.assertEqual(exp_return, act_return)

    # Tests for get_config.
    def test_get_config_in_cwd(self):
        """If no path is given, check if there is a config file in
        the current working directory. If there is, return the mkname
        section from that config.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        src = self.test_config_loc
        dst = self.local_config_loc
        shutil.copy2(src, dst)

        # Run test.
        act = mn.get_config()

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_get_config_with_file_as_str(self):
        """Given the path to a configuration file as a string,
        return the mkname configuration found in that file.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        path_str = self.test_config_loc

        # Run test.
        act = mn.get_config(path_str)

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_get_config_with_file_as_path(self):
        """Given the path to a configuration file as a string,
        return the mkname configuration found in that file.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        path_str = self.test_config_loc
        path = Path(path_str)

        # Run test.
        act = mn.get_config(path)

        # Determine test result.
        self.assertConfigEqual(exp, act)


@ut.skip
class OldInitializationTestCase(ut.TestCase):
    def assertConfigEqual(self, a: Mapping, b: Mapping) -> None:
        """Assert that two ParserConfig objects are equal."""
        a_keylist = list(a.keys())
        b_keylist = list(b.keys())
        self.assertListEqual(a_keylist, b_keylist)
        for key in a:
            if not isinstance(a[key], str):
                self.assertConfigEqual(a[key], b[key])
            else:
                self.assertEqual(a[key], b[key])

    def tearDown(self):
        """Post-test clean up."""
        path_strs = [
            LOCAL_CONFIG,
            LOCAL_DB,
        ]
        paths = [Path(s) for s in path_strs]
        for path in paths:
            if path.is_file():
                path.unlink()

    def test_init_config(self):
        """If a config file doesn't exist for mkname in the current
        working directory, create it using the package's default
        configuration and return that the file was created.
        """
        # Expected value.
        exp_status = 'created'
        with open('mkname/data/defaults.cfg') as fh:
            exp_file = fh.read()

        # Test data and state.
        filepath = LOCAL_CONFIG
        path = Path(filepath)
        if path.is_file():
            msg = f'{filepath} exists.'
            raise RuntimeError(msg)

        # Run test.
        act_status = mn.init_config()

        # Gather actual data.
        with open(filepath) as fh:
            act_file = fh.read()

        # Determine test result.
        self.assertEqual(exp_status, act_status)
        self.assertEqual(exp_file, act_file)

    def test_init_config_already_exists(self):
        """If the local config file already exists in the current
        working directory, return that it exists.
        """
        # Expected value.
        exp = 'exists'

        # Test data and state.
        src = 'mkname/data/defaults.cfg'
        dst = LOCAL_CONFIG
        shutil.copy2(src, dst)
        act_path = Path(dst)

        # Run test.
        act = mn.init_config()

        # Determine test result.
        self.assertEqual(exp, act)
        self.assertTrue(act_path.is_file())

    def test_init_db(self):
        """If a name database doesn't exist for mkname in the current
        working directory, create it using the package's default
        name database and return that the database was created.
        """
        # Expected values.
        exp_status = 'created'
        with open('mkname/data/names.db', 'rb') as fh:
            exp_file = fh.read()

        # Test data and state.
        filepath = LOCAL_DB
        path = Path(filepath)
        if path.is_file():
            msg = f'{filepath} exists.'
            raise RuntimeError(msg)

        # Run test.
        act_status = mn.init_db()

        # Gather actual data.
        with open(filepath, 'rb') as fh:
            act_file = fh.read()

        # Determine test result.
        self.assertEqual(exp_status, act_status)
        self.assertEqual(exp_file, act_file)

    def test_init_db_already_exists(self):
        """If the local database file already exists in the current
        working directory, return that it exists.
        """
        # Expected value.
        exp = 'exists'

        # Test data and state.
        src = 'mkname/data/names.db'
        dst = LOCAL_DB
        shutil.copy2(src, dst)
        act_path = Path(dst)

        # Run test.
        act = mn.init_db()

        # Determine test result.
        self.assertEqual(exp, act)
        self.assertTrue(act_path.is_file())

    # Tests for load_config.
    def test_load_config(self):
        """When called, load_config() should return a mapping that
        contains the mkname configuration from the given configuration
        file.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        config_path = 'tests/data/test_load_config.conf'

        # Run test.
        act = mn.load_config(config_path)

        # Determine test result.
        self.assertConfigEqual(exp, act)

    def test_load_config_uninitialized(self):
        """If the given configuration file doesn't exist, load_config()
        should create it with the default settings.
        """
        # Expected values.
        exp_path = Path(LOCAL_CONFIG)
        exp_return = {
            'db_path': 'mkname/data/names.db',
        }

        # Test data and state.
        if exp_path.exists():
            msg = f'{exp_path} exists.'
            raise RuntimeError(msg)

        # Run test.
        act_return = mn.load_config(exp_path)

        # Determine test result.
        self.assertTrue(exp_path.is_file())
        self.assertConfigEqual(exp_return, act_return)
