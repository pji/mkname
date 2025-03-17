"""
test_cli
~~~~~~~~

Unit tests for mkname.cli.
"""
import os
from itertools import permutations
from pathlib import Path

import pytest

from mkname import cli
from mkname import constants as c
from mkname import init
from mkname import mkname as mn
from tests.common import *
from tests.fixtures import *


# Fixtures.
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


def tools_cli_test(mocker, capsys, cmd):
    """Run a standard test of the CLI."""
    mocker.patch('sys.argv', cmd)
    cli.parse_mkname_tools()
    captured = capsys.readouterr()
    return captured.out


# Test cases.
class TestMkname:
    def test_build_compound_name(self, mocker, capsys, test_db):
        """When called with the -c option, construct a name from
        compounding two names from the database.
        """
        cmd = ['python -m mkname', '-c']
        roll = [3, 2]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'Tam\n'

    def test_build_syllable_name(self, mocker, capsys, test_db):
        """When called with the -s 3 option, construct a name from
        a syllable from three names in the database.
        """
        cmd = ['python -m mkname', '-s 3']
        roll = [3, 2, 4, 2, 1, 1]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'Athamwaff\n'

    def test_build_syllable_name_4_syllables(self, mocker, capsys, test_db):
        """When called with the -s 4 option, construct a name from
        a syllable from four names in the database.
        """
        cmd = ['python -m mkname', '-s 4']
        roll = [3, 2, 4, 1, 2, 1, 1, 1]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'Athamwaffspam\n'

    def test_build_syllable_name_diff_consonants(
        self, mocker, capsys, testletters
    ):
        """The consonants and vowels from the config should affect
        how the name is generated.
        """
        cmd = ['python -m mkname', '-s 1']
        roll = [4, 1]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'Waf\n'

    def test_make_multiple_names(self, mocker, capsys, test_db):
        """When called with the -n 3 option, create three names."""
        cmd = ['python -m mkname', '-n', '3']
        roll = [3, 1, 4]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == (
            'tomato\n'
            'spam\n'
            'waffles\n'
        )

    def test_modify_name(self, mocker, capsys, test_db):
        """When called with the -m garble option, perform the garble
        mod on the name.
        """
        cmd = ['python -m mkname', '-m', 'garble']
        roll = [3, 5]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'Tomadao\n'

    def test_pick_name(self, mocker, capsys, test_db):
        """When called with the -p option, select a random name
        from the list of names.
        """
        cmd = ['python -m mkname',]
        roll = [3,]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'tomato\n'

    def test_use_config(self, mocker, capsys, conf_path):
        """When called with the -C option followed by a path to a
        configuration file, use the configuration in that file when
        running the script.
        """
        cmd = [
            'python -m mkname',
            '-C', str(conf_path),
        ]
        roll = [3,]
        result = cli_test(mocker, capsys, cmd, roll)
        assert result == 'tomato\n'


class TestMknameAdd:
    def test_add(self, mocker, capsys, name, names, tmp_db):
        """Given a database and information for a name,
        `mkname_tools add` should add the name to the
        given database.
        """
        cmd = [
            'mkname_tool', 'add',
            str(tmp_db),
            '-n', name.name,
            '-s', name.source,
            '-c', name.culture,
            '-d', str(name.date),
            '-g', name.gender,
            '-k', name.kind,
        ]
        exp_msg = c.MSGS['en']['add_success'].format(
            name=name.name,
            dst_path=tmp_db
        )
        assert tools_cli_test(mocker, capsys, cmd)
        assert db_matches_names(tmp_db, [*names, name])

    def test_cannot_write_to_default_db(
        self, mocker, capsys, name, names, prot_db
    ):
        """When given the path to the default database,
        `mkname_tools add` will return an error message
        and not write to the default database.
        """
        cmd = [
            'mkname_tool', 'add',
            str(prot_db),
            '-n', name.name,
            '-s', name.source,
            '-c', name.culture,
            '-d', str(name.date),
            '-g', name.gender,
            '-k', name.kind,
        ]
        exp_msg = c.MSGS['en']['add_default_db'] + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(prot_db, names)


class TestMknameToolsCopy:
    def test_copy_default(
        self, mocker, capsys, names, test_db, run_in_tmp
    ):
        """When invoked, `mkname_tools copy` should create a copy
        of the default names database in the current working directory.
        """
        new_path = run_in_tmp / 'names.db'
        cmd = ['mkname_tools', 'copy',]
        exp_msg = f'The database has been copied to {new_path.absolute()}.\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(new_path, names)

    def test_to_file(
        self, mocker, capsys, names, test_db, tmp_path
    ):
        """When invoked with `-o` and the path to save the db copy to,
        `mkname_tools copy` should create a copy of the default names
        database in the given path.
        """
        path = tmp_path / 'names.db'
        cmd = [
            'mkname_tools', 'copy',
            '-o', str(path),
        ]
        exp_msg = f'The database has been copied to {path.absolute()}.\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, names)

    def test_will_not_overwrite(self, mocker, capsys, test_db, tmp_path):
        """When pointed to a path with an existing file, `mkname_tools`
        should print an error message and not overwrite the file.
        """
        text = 'spam'
        path = tmp_path / 'spam'
        path.write_text('spam')
        cmd = [
            'mkname_tools', 'copy',
            '-o', str(path),
        ]
        exp_msg = c.MSGS['en']['dup_path_exists'].format(dst_path=path) + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert file_matched_text(path, text)

    def test_will_make_file_in_directory(
        self, mocker, capsys, names, test_db, tmp_path
    ):
        """When pointed to a directory, `mkname_tools` should create
        the `names.db` in the directory.
        """
        path = tmp_path / 'names.db'
        cmd = [
            'mkname_tools', 'copy',
            '-o', str(tmp_path),
        ]
        exp_msg = f'The database has been copied to {path.absolute()}.\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, names)


class TestMknameToolsExport:
    def test_default(
        self, mocker, capsys, names, test_db, run_in_tmp, tmp_path
    ):
        """When no options are passed, `mknname_tools export`
        should export the contents of the default database to
        a CSV file named `names.csv`.
        """
        csv_path = Path('./names.csv')
        cmd = ['mkname_tools', 'export',]
        exp_msg = f'Database exported to {csv_path}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert csv_matches_names(csv_path, names)

    def test_output(self, mocker, capsys, names, test_db, tmp_path):
        """When `-o` and a path is passed, `mknname_tools export`
        should export the contents of the default database to
        a CSV at the given path`.
        """
        csv_path = tmp_path / 'spam.csv'
        assert not csv_path.exists()
        cmd = ['mkname_tools', 'export', '-o', str(csv_path)]
        exp_msg = f'Database exported to {csv_path}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert csv_matches_names(csv_path, names)

    def test_output_with_config(
        self, mocker, capsys, conf_path, names, tmp_path
    ):
        """When `-o` and a path and `-f` and a path is passed,
        `mknname_tools export` should export the contents of
        the database in the configuration file to a CSV at the
        given path`.
        """
        csv_path = tmp_path / 'spam.csv'
        assert not csv_path.exists()
        cmd = [
            'mkname_tools',
            '-f', f'{conf_path}',
            'export',
            '-o', f'{csv_path}',
        ]
        exp_msg = f'Database exported to {csv_path}.\n\n'
        try:
            assert tools_cli_test(mocker, capsys, cmd) == exp_msg
            assert csv_matches_names(csv_path, names)
        except Exception as ex:
            raise ex
        else:
            csv_path.unlink()


class TestMknameToolsImport:
    def test_cannot_write_to_default_db(
        self, mocker, capsys, csv_path, names, tmp_empty_db
    ):
        """When not given the path to a name database,
        `mkname_tools import` will return an error message
        and not write to the default database.
        """
        cmd = [
            'mkname_tools', 'import',
            '-i', str(csv_path),
            '-o', str(init.get_default_db()),
        ]
        exp_msg = f'Cannot import to the default database.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(tmp_empty_db, [])

    def test_csv_to_existing_db(
        self, mocker, capsys, csv_path, empty_db, names,
    ):
        """When passed `-i` and the path to a CSV file and a `-o` and
        the path to a name database, `mkname_tools import` should import
        the contents of the CSV file into the database.
        """
        cmd = [
            'mkname_tools', 'import',
            '-i', str(csv_path),
            '-o', str(empty_db)
        ]
        exp_msg = f'Imported {csv_path} to {empty_db}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(empty_db, names)

    def test_csv_to_new_db(
        self, mocker, capsys, csv_path, names, tmp_path
    ):
        """When passed `-i` and the path to a CSV file and a `-o` and
        the path to a nonexistent database, `mkname_tools import` should
        create that database and import the contents of the CSV file
        into the database.
        """
        path = tmp_path / 'spam'
        cmd = [
            'mkname_tools', 'import',
            '-i', str(csv_path),
            '-o', str(path)
        ]
        exp_msg = f'Imported {csv_path} to {path}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, names)

    def test_census_gov_to_existing_db(
        self, mocker, capsys, census_gov_surnames_path, empty_db,
        census_gov_surnames_names
    ):
        """When passed `-i` and the path to a census.name file, a
        `-o` and the path to a name database, a `-f` and `census_name`,
        `-s` and a source, `-d` and a date, a `-g` and a gender,
        and `-k` and a kind, `mkname_tools import` should import the
        contents of the census.gov file into the database.
        """
        cmd = [
            'mkname_tools', 'import',
            '-i', str(census_gov_surnames_path),
            '-o', str(empty_db),
            '-f', 'census.gov',
            '-s', 'census.gov',
            '-d', '2010',
            '-k', 'surname',
        ]
        exp_msg = f'Imported {census_gov_surnames_path} to {empty_db}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(empty_db, census_gov_surnames_names)

    def test_census_name_to_existing_db(
        self, mocker, capsys, census_name_given_path, empty_db,
        census_name_given_names
    ):
        """When passed `-i` and the path to a census.name file, a
        `-o` and the path to a name database, a `-f` and `census_name`,
        `-s` and a source, `-d` and a date, and `-k` and a kind,
        `mkname_tools import` should import the contents of the
        census.name file into the database.
        """
        cmd = [
            'mkname_tools', 'import',
            '-i', str(census_name_given_path),
            '-o', str(empty_db),
            '-f', 'census.name',
            '-s', 'census.name',
            '-d', '2025',
            '-k', 'given'
        ]
        exp_msg = f'Imported {census_name_given_path} to {empty_db}.\n\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(empty_db, census_name_given_names)


class TestMknameToolsList:
    def test_all_names(self, mocker, capsys, test_db):
        """When called with no options, write all the names from
        the database to standard out.
        """
        cmd = ['python -m mkname', 'list']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'ham\n'
            'tomato\n'
            'waffles\n'
        )

    def test_all_names_in_given_db(self, mocker, capsys, db_path):
        """When called with `-d` and the path to a database, write
        all the names from the database to standard out.
        """
        cmd = ['mkname_tools', 'list', '-d', str(db_path)]
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'ham\n'
            'tomato\n'
            'waffles\n'
        )

    def test_all_names_with_config(self, mocker, capsys, conf_path):
        """When called with `-f` and the path to a config file,
        write all the names from the configured database to
        standard out.
        """
        cmd = [
            'mkname_tools',
            '-f', str(conf_path),
            'list',
        ]
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'ham\n'
            'tomato\n'
            'waffles\n'
        )

    def test_culture(self, mocker, capsys, test_db):
        """When called with the -k option and a culture, use only
        names from that culture for the list.
        """
        cmd = ['mkname_tools', 'list', '-c', 'bacon']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'ham\n'
        )

    def test_gender(self, mocker, capsys, test_db):
        """When called with the -k option and a culture, use only
        names from that culture for the generation.
        """
        cmd = ['mkname_tools', 'list', '-g', 'sausage']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'tomato\n'
        )

    def test_kinds(self, mocker, capsys, test_db):
        """When called with the -k option and a kind of name, use
        only given names for the generation.
        """
        cmd = ['mkname_tools', 'list', '-k', 'given',]
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'spam\n'
            'ham\n'
            'waffles\n'
        )

    def test_list_cultures(self, mocker, capsys, test_db):
        """When called with -C, write the unique cultures from the
        database to standard out.
        """
        cmd = ['mkname_tools', 'list', '-C']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'bacon\n'
            'pancakes\n'
            'porridge\n'
        )

    def test_list_genders(self, mocker, capsys, test_db):
        """When called with -G, write the unique genders from the
        database to standard out.
        """
        cmd = ['mkname_tools', 'list', '-G']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'sausage\n'
            'baked beans\n'
        )

    def test_list_kinds(self, mocker, capsys, test_db):
        """When called with -K, write the unique kinds from the
        database to standard out.
        """
        cmd = ['mkname_tools', 'list', '-K']
        result = tools_cli_test(mocker, capsys, cmd)
        assert result == (
            'given\n'
            'surname\n'
        )


class TestMknameToolsNew:
    def test_default(
        self, mocker, capsys, test_db, run_in_tmp
    ):
        """When invoked, `mkname_tools new` should create an empty
        names database in the current working directory.
        """
        path = run_in_tmp / 'names.db'
        cmd = ['mkname_tools', 'new',]
        exp_msg = c.MSGS['en']['new_success'].format(
            dst_path=str(path.absolute())
        ) + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, [])

    def test_to_file(self, mocker, capsys, test_db, tmp_path):
        """When invoked with `-o` and the path to save the db copy to,
        `mkname_tools new` should create a copy of the default names
        database in the given path.
        """
        path = tmp_path / 'names.db'
        cmd = [
            'mkname_tools', 'new',
            '-o', str(path),
        ]
        exp_msg = c.MSGS['en']['new_success'].format(
            dst_path=str(path.absolute())
        ) + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, [])

    def test_will_not_overwrite(self, mocker, capsys, test_db, tmp_path):
        """When pointed to a path with an existing file, `mkname_tools`
        should print an error message and not overwrite the file.
        """
        text = 'spam'
        path = tmp_path / 'spam'
        path.write_text('spam')
        cmd = [
            'mkname_tools', 'new',
            '-o', str(path),
        ]
        exp_msg = c.MSGS['en']['new_path_exists'].format(dst_path=path) + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert file_matched_text(path, text)

    def test_will_make_file_in_directory(
        self, mocker, capsys, test_db, tmp_path
    ):
        """When pointed to a directory, `mkname_tools` should create
        the `names.db` in the directory.
        """
        path = tmp_path / 'names.db'
        cmd = [
            'mkname_tools', 'new',
            '-o', str(tmp_path),
        ]
        exp_msg = c.MSGS['en']['new_success'].format(
            dst_path=str(path.absolute())
        ) + '\n'
        assert tools_cli_test(mocker, capsys, cmd) == exp_msg
        assert db_matches_names(path, [])
