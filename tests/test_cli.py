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
        self.original_defaults = c.DEFAULT_CONFIG_DATA
        c.DEFAULT_CONFIG_DATA['db_path'] = 'tests/data/names.db'

    def tearDown(self):
        sys.argv = self.original_args
        c.DEFAULT_CONFIG_DATA = self.original_defaults

    @patch('mkname.mkname.roll')
    def test_build_compound_name(self, mock_roll):
        """When called with the -c option, construct a name from
        compounding two names from the database.
        """
        # Expected value.
        exp = 'Tam\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-c']
        mock_roll.side_effect = [3, 2]
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll')
    def test_build_syllable_name(self, mock_roll):
        """When called with the -s 3 option, construct a name from
        a syllable from three names in the database.
        """
        # Expected value.
        exp = 'Athamwaff\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-s 3']
        mock_roll.side_effect = [3, 2, 4, 2, 1, 1]
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll')
    def test_build_syllable_name_4_syllables(self, mock_roll):
        """When called with the -s 4 option, construct a name from
        a syllable from four names in the database.
        """
        # Expected value.
        exp = 'Athamwaffspam\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-s', '4']
        mock_roll.side_effect = [3, 2, 4, 1, 2, 1, 1, 1]
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll')
    def test_build_syllable_name_diff_consonants(self, mock_roll):
        """The consonants and vowels from the config should affect
        how the name is generated.
        """
        # Expected value.
        exp = 'Waf\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-s 1']
        c.DEFAULT_CONFIG_DATA['consonants'] = 'bcdfghjkmnpqrstvwxz'
        c.DEFAULT_CONFIG_DATA['vowels'] = 'aeiouyl'
        mock_roll.side_effect = [4, 1]
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    def test_first_names(self):
        """When called with the -F option, use only given names for
        the generation.
        """
        # Expected value.
        names = (
            'spam',
            'ham',
            'waffles',
            '',
        )
        exp = '\n'.join(names)

        # Test data and state.
        sys.argv = ['python -m mkname', '-L', '-f']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    def test_last_name(self):
        """When called with -l, only use surnames for the generation."""
        # Expected value.
        exp = 'tomato\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-L', '-l']
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

    def test_list_cultures(self):
        """When called with -K, write the unique cultures from the
        database to standard out.
        """
        # Expected value.
        cultures = (
            'bacon',
            'pancakes',
            'porridge',
            '',
        )
        exp = '\n'.join(cultures)

        # Test data and state.
        sys.argv = ['python -m mkname', '-K']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll')
    def test_make_multiple_names(self, mock_roll):
        """When called with the -n 3 option, create three names."""
        # Expected value.
        exp = (
            'tomato\n'
            'spam\n'
            'waffles\n'
        )

        # Test data and state.
        sys.argv = ['python -m mkname', '-p', '-n', '3']
        mock_roll.side_effect = [3, 1, 4]
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

    @patch('mkname.mkname.roll', return_value=3)
    @patch('mkname.mod.roll', return_value=5)
    def test_modify_name(self, _, __):
        """When called with the -m garble option, perform the garble
        mod on the name.
        """
        # Expected value.
        exp = 'Tomadao\n'

        # Test data and state.
        sys.argv = ['python -m mkname', '-p', '-m', 'garble']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)

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

    def test_use_config(self):
        """When called with the -C option followed by a path to a
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
            '-C', 'tests/data/test_use_config.cfg',
            '-L'
        ]
        c.DEFAULT_CONFIG_DATA['db_path'] = self.original_defaults['db_path']
        with patch('sys.stdout', new=StringIO()) as mock_out:

            # Run test
            cli.parse_cli()

            # Gather actual value.
            act = mock_out.getvalue()

        # Determine test result.
        self.assertEqual(exp, act)
