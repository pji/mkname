"""
fixtures
~~~~~~~~

Common fixtures for :mod:`mkname` tests.
"""
import os
import sqlite3
from pathlib import Path

import pytest as pt

import mkname.model as m


__all__ = [
    'census_gov_surnames_names',
    'census_gov_surnames_path',
    'census_name_given_path',
    'census_name_given_names',
    'csv_path',
    'conf_path',
    'db_path',
    'empty_db',
    'names',
    'run_in_tmp',
    'prot_db',
    'test_db',
    'tmp_db',
    'tmp_empty_db',
]


@pt.fixture
def census_gov_surnames_names():
    src = 'census.gov'
    date = 2010
    kind = 'surname'
    gender = 'none'
    culture = 'United States'
    data = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones',]
    return tuple(
        m.Name(i, name, src, culture, date, gender, kind)
        for i, name in enumerate(data)
    )


@pt.fixture
def census_gov_surnames_path():
    return 'tests/data/us_census_surnames.tsv'


@pt.fixture
def census_name_given_names():
    src = 'census.name'
    date = 2025
    kind = 'given'
    data = [
        ['Сергей', 'Russia', 'male',],
        ['Анна', 'Russia', 'female',],
        ['Björn', 'Germany', 'male',],
        ['Jürgen', 'Germany', 'male',],
        ['Hélène', 'France', 'female',],
    ]
    return tuple(
        m.Name(i, name[0], src, name[1], date, name[2], kind)
        for i, name in enumerate(data)
    )


@pt.fixture
def census_name_given_path():
    return 'tests/data/census_name.csv'


@pt.fixture
def conf_path():
    return 'tests/data/test_use_config.cfg'


@pt.fixture
def csv_path():
    return 'tests/data/serialized_names.csv'


@pt.fixture
def db_path():
    return 'tests/data/names.db'


@pt.fixture
def empty_db(tmp_path):
    db_path = tmp_path / 'empty.db'

    # Create the names table.
    con = sqlite3.Connection(db_path)
    cur = con.cursor()
    cur.execute((
        'CREATE TABLE names(\n'
        '    id          integer primary key autoincrement,\n'
        '    name        char(64),\n'
        '    source      char(128),\n'
        '    culture     char(64),\n'
        '    date        integer,\n'
        '    gender      char(64),\n'
        '    kind        char(16)\n'
        ')\n'
    ))
    con.close

    yield db_path


@pt.fixture
def names():
    """The contents of the test database."""
    yield (
        m.Name(
            1,
            'spam',
            'eggs',
            'bacon',
            1970,
            'sausage',
            'given'
        ),
        m.Name(
            2,
            'ham',
            'eggs',
            'bacon',
            1970,
            'baked beans',
            'given'
        ),
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
        m.Name(
            4,
            'waffles',
            'mushrooms',
            'porridge',
            2000,
            'baked beans',
            'given'
        ),
    )


@pt.fixture
def prot_db(mocker, db_path, tmp_path):
    """Point the default db to a temporary copy of the test db."""
    path = Path(db_path)
    cp_path = Path(tmp_path / 'names.db')
    data = path.read_bytes()
    cp_path.write_bytes(data)
    mocker.patch('mkname.db.get_db', return_value=cp_path)
    yield tmp_db


@pt.fixture
def run_in_tmp(tmp_path):
    """Run the test while the current working directory is in
    a temp director.
    """
    home = Path.cwd()
    os.chdir(tmp_path)
    yield None
    os.chdir(home)


@pt.fixture
def test_db(mocker):
    """Point the default database to the test database."""
    db_path = Path.cwd() / 'tests/data/names.db'
    mocker.patch('mkname.init.get_default_db', return_value=db_path)
    yield None


@pt.fixture
def tmp_db(db_path, tmp_path):
    """Create a temp copy of the default database."""
    path = Path(db_path)
    cp_path = Path(tmp_path / 'names.db')
    data = path.read_bytes()
    cp_path.write_bytes(data)
    yield cp_path


@pt.fixture
def tmp_empty_db(mocker, empty_db):
    """Point the default database to an empty database."""
    mocker.patch('mkname.init.get_default_db', return_value=empty_db)
    yield empty_db
