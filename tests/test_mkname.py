"""
test_mkname
~~~~~~~~~~~
"""
import configparser
import filecmp
from pathlib import Path
import shutil

import pytest

from mkname import mkname as mn
from mkname.constants import *
from mkname.model import Name


# Fixtures.
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
