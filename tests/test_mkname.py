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
