"""
test_cli
~~~~~~~~

Unit tests for mkname.cli.
"""
from io import StringIO
import unittest as ut
from unittest.mock import patch
import sys

from mkname import cli
from mkname import constants as c


# Test cases.
class CommandLineOptionTestCase(ut.TestCase):
    def setUp(self):
        self.original_args = sys.argv
        self.original_db_loc = c.DEFAULT_CONFIG_DATA['db_path']
        c.DEFAULT_CONFIG_DATA['db_path'] = 'tests/data/names.db'

    def tearDown(self):
        sys.argv = self.original_args
        c.DEFAULT_CONFIG_DATA['db_path'] = self.original_db_loc

    @patch('mkname.mkname.roll', return_value=3)
    def test_pick_name(self, _):
        """When called with the -p option, select a random name
        from the list of names.
        """
        # Expected value.
        exp = 'tomato\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-p']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    def test_list_all_names(self):
        """When called with the -L option, write all the names from
        the database to standard out.
        """
        # Expected value.
        names = (
            'spam',
            'ham',
            'tomato',
            'waffles',
            '',
        )
        exp = '\n'.join(names)

        # Test data and state.
        sys.argv = ['python -m mkname', '-L']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    def test_use_config(self):
        """When called with the -c option followed by a path to a
        configuration file, use the configuration in that file when
        running the script.
        """
        # Expected value.
        names = (
            'spam',
            'ham',
            'tomato',
            'waffles',
            '',
        )
        exp = '\n'.join(names)

        # Test data and state.
        sys.argv = [
            'python -m mkname',
            '-c', 'tests/data/test_use_config.cfg',
            '-L'
        ]
        c.DEFAULT_CONFIG_DATA['db_path'] = self.original_db_loc
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)
