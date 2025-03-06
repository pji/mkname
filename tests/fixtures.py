"""
fixtures
~~~~~~~~

Common fixtures for :mod:`mkname` tests.
"""
import sqlite3

import pytest as pt

import mkname.model as m


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
def test_db(mocker, tmp_path):
    """Point the default database to the test database."""
    db_path = 'tests/data/names.db'
    mocker.patch('mkname.db.get_db', return_value=db_path)
    yield None
