"""
test_mkname
~~~~~~~~~~~
"""
import configparser
import filecmp
import shutil
from pathlib import Path

import pytest

from mkname import mkname as mn
from mkname.constants import *
from mkname.model import Name


# Fixtures.
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
class TestBuildCompoundNames:
    def test_build_compound_name(self, names, mocker):
        """Given a sequence of names, build_compound_name() returns a
        name constructed from the list.
        """
        mocker.patch('yadr.roll', side_effect=[4, 3])
        assert mn.build_compound_name_from_names(names) == 'Dallory'


def test_build_from_syllables(names, mocker):
    """Given a sequence of names, return a name build from one
    syllable from each name.
    """
    mocker.patch('yadr.roll', side_effect=[2, 1, 5, 2, 1, 3])
    num_syllables = 3
    assert mn.build_syllable_name_from_names(
        num_syllables, names
    ) == 'Ertalan'


class TestSelectRandomName:
    def test_select_random_name(self, names, mocker):
        """Given a list of names, return a random name."""
        mocker.patch('yadr.roll', side_effect=[4,])
        assert mn.select_name_from_names(names) == 'Donatello'
