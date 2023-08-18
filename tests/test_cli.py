"""
test_cli
~~~~~~~~

Unit tests for mkname.cli.
"""
import pytest

from mkname import cli
from mkname import constants as c
from mkname import mkname as mn
from mkname import init


# Fixtures.
@pytest.fixture
def testdb(mocker):
    """Point the unit test to the test instance of the database."""
    config = init.get_config()
    config['mkname']['db_path'] = 'tests/data/names.db'
    mocker.patch('mkname.cli.get_config', return_value=config)


@pytest.fixture
def testletters(mocker):
    """Change the consonants and vowels for a test."""
    config = init.get_config()
    config['mkname']['db_path'] = 'tests/data/names.db'
    config['mkname']['consonants'] = 'bcdfghjkmnpqrstvwxz'
    config['mkname']['vowels'] = 'aeiouyl'
    mocker.patch('mkname.cli.get_config', return_value=config)


# Core test functions.
def cli_test(mocker, capsys, cmd, roll=None):
    """Run a standard test of the CLI."""
    mocker.patch('sys.argv', cmd)
    if roll:
        mocker.patch('yadr.roll', side_effect=roll)

    cli.parse_cli()

    captured = capsys.readouterr()
    return captured.out


# Test cases.
def test_build_compound_name(mocker, capsys, testdb):
    """When called with the -c option, construct a name from
    compounding two names from the database.
    """
    cmd = ['python -m mkname', '-c']
    roll = [3, 2]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'Tam\n'


def test_build_syllable_name(mocker, capsys, testdb):
    """When called with the -s 3 option, construct a name from
    a syllable from three names in the database.
    """
    cmd = ['python -m mkname', '-s 3']
    roll = [3, 2, 4, 2, 1, 1]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'Athamwaff\n'


def test_build_syllable_name_4_syllables(mocker, capsys, testdb):
    """When called with the -s 4 option, construct a name from
    a syllable from four names in the database.
    """
    cmd = ['python -m mkname', '-s 4']
    roll = [3, 2, 4, 1, 2, 1, 1, 1]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'Athamwaffspam\n'


def test_build_syllable_name_diff_consonants(
    mocker, capsys, testletters
):
    """The consonants and vowels from the config should affect
    how the name is generated.
    """
    cmd = ['python -m mkname', '-s 1']
    roll = [4, 1]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'Waf\n'


def test_culture(mocker, capsys, testdb):
    """When called with the -k option and a culture, use only
    names from that culture for the generation.
    """
    cmd = ['python -m mkname', '-L', '-k', 'bacon']
    result = cli_test(mocker, capsys, cmd)
    assert result == (
        'spam\n'
        'ham\n'
    )


def test_first_names(mocker, capsys, testdb):
    """When called with the -F option, use only given names for
    the generation.
    """
    cmd = ['python -m mkname', '-L', '-f']
    result = cli_test(mocker, capsys, cmd)
    assert result == (
        'spam\n'
        'ham\n'
        'waffles\n'
    )


def test_last_name(mocker, capsys, testdb):
    """When called with -l, only use surnames for the generation."""
    cmd = ['python -m mkname', '-L', '-l']
    result = cli_test(mocker, capsys, cmd)
    assert result == 'tomato\n'


def test_list_all_names(mocker, capsys, testdb):
    """When called with the -L option, write all the names from
    the database to standard out.
    """
    cmd = ['python -m mkname', '-L']
    result = cli_test(mocker, capsys, cmd)
    assert result == (
        'spam\n'
        'ham\n'
        'tomato\n'
        'waffles\n'
    )


def test_list_cultures(mocker, capsys, testdb):
    """When called with -K, write the unique cultures from the
    database to standard out.
    """
    cmd = ['python -m mkname', '-K']
    result = cli_test(mocker, capsys, cmd)
    assert result == (
        'bacon\n'
        'pancakes\n'
        'porridge\n'
    )


def test_make_multiple_names(mocker, capsys, testdb):
    """When called with the -n 3 option, create three names."""
    cmd = ['python -m mkname', '-p', '-n', '3']
    roll = [3, 1, 4]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == (
        'tomato\n'
        'spam\n'
        'waffles\n'
    )


def test_modify_name(mocker, capsys, testdb):
    """When called with the -m garble option, perform the garble
    mod on the name.
    """
    cmd = ['python -m mkname', '-p', '-m', 'garble']
    roll = [3, 5]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'Tomadao\n'


def test_pick_name(mocker, capsys, testdb):
    """When called with the -p option, select a random name
    from the list of names.
    """
    cmd = ['python -m mkname', '-p']
    roll = [3,]
    result = cli_test(mocker, capsys, cmd, roll)
    assert result == 'tomato\n'


def test_use_config(mocker, capsys):
    """When called with the -C option followed by a path to a
    configuration file, use the configuration in that file when
    running the script.
    """
    cmd = [
        'python -m mkname',
        '-C', 'tests/data/test_use_config.cfg',
        '-L'
    ]
    result = cli_test(mocker, capsys, cmd)
    assert result == (
        'spam\n'
        'ham\n'
        'tomato\n'
        'waffles\n'
    )
