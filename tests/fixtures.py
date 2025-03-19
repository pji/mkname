"""
fixtures
~~~~~~~~

Common fixtures for :mod:`mkname` tests.
"""
import os
import sqlite3
from configparser import ConfigParser
from pathlib import Path

import pytest as pt

import mkname.model as m


__all__ = [
    'census_gov_surnames_names',
    'census_gov_surnames_path',
    'census_name_given_path',
    'census_name_given_names',
    'change_db',
    'conf_path',
    'conf_full_path',
    'csv_path',
    'db_path',
    'empty_db',
    'name',
    'names',
    'run_in_tmp',
    'run_in_tmp_with_db',
    'prot_db',
    'setup_conf',
    'test_conf',
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
def change_db(tmp_path):
    """A temporary database to update."""
    path = Path('tests/data/names_to_change.db')
    cp_path = Path(tmp_path / 'names_to_change.db')
    data = path.read_bytes()
    cp_path.write_bytes(data)
    return cp_path


@pt.fixture
def conf_path():
    """Path to a partial config file for testing."""
    return Path.cwd() / 'tests/data/test_use_config.cfg'


@pt.fixture
def conf_full_path():
    """Path to a full config file for testing."""
    return Path.cwd() / 'tests/data/test_load_config.conf'


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
def name():
    return m.Name(
        id=5,
        name='Graham',
        source='https://montypython.com/',
        culture='Monty Python',
        date=1941,
        gender='male',
        kind='given'
    )


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
    mocker.patch('mkname.init.get_default_db', return_value=cp_path)
    yield cp_path


@pt.fixture
def run_in_tmp(tmp_path):
    """Run the test while the current working directory is in
    a temp director.
    """
    home = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(home)


@pt.fixture
def run_in_tmp_with_db(db_path, tmp_path):
    """Run the test in a temporary directory with a names db
    in that directory.
    """
    o_path = Path(db_path)
    cp_path = tmp_path / 'names.db'
    data = o_path.read_bytes()
    cp_path.write_bytes(data)

    home = Path.cwd()
    os.chdir(tmp_path)
    yield cp_path
    os.chdir(home)


@pt.fixture
def setup_conf(conf_full_path, tmp_path):
    """Run the test from a temporary directory with config in a
    `setup.cfg` file.
    """
    home = Path.cwd()

    cp_path = tmp_path / 'setup.cfg'
    src_path = Path(conf_full_path)
    text = src_path.read_text()
    cp_path.write_text(text)

    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(home)


@pt.fixture
def test_conf(mocker, conf_full_path):
    """Point the default config to the test config."""
    parser = ConfigParser()
    parser.read(conf_full_path)
    sections = ['mkname', 'mkname_files']
    mocker.patch('mkname.init.get_config', return_value={
        k: dict(parser[k]) for k in parser
        if k in sections
    })
    yield conf_path


@pt.fixture
def test_db(mocker):
    """Point the default database to the test database."""
    db_path = Path.cwd() / 'tests/data/names.db'
    mocker.patch('mkname.init.get_default_db', return_value=db_path)
    yield db_path


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
