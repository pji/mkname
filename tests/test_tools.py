"""
test_tools
~~~~~~~~~~

Unit tests for :mod:`mkname.tools`.
"""
import csv

import pytest

import mkname.model as m
import mkname.tools as t


# Fixtures.
@pytest.fixture
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


# Test cases.
class TestReadCSV:
    def test_read(self, names):
        """Given a path to a CSV with serialized :class:`mkname.model.Name`
        objects, :func:`mkname.tools.read_csv` should read the file and
        return the names as a :class:`tuple` of :class:`mkname.model.Name`
        objects.
        """
        path = 'tests/data/serialized_names.csv'
        actual = t.read_csv(path)
        assert actual == names

    def test_read_no_ids(self, names):
        """Given a path to a CSV with serialized :class:`mkname.model.Name`
        objects that don't have ids, :func:`mkname.tools.read_csv` should
        read the file and return the names as a :class:`tuple` of
        :class:`mkname.model.Name` objects. If the serialized names
        don't have IDs, they should be given IDs when they are created.
        """
        names = tuple(m.Name(0, *name.astuple()[1:]) for name in names)
        path = 'tests/data/serialized_names_no_id.csv'
        actual = t.read_csv(path)
        assert actual == names

    def test_does_not_exist(self):
        """Given a path that doesn't exist, :func:`mkname.tools.read_csv`
        should raise a PathDoesNotExistError.
        """
        path = 'tests/data/__spam.eggs'
        with pytest.raises(t.PathDoesNotExistError):
            t.read_csv(path)


def test_reindex(names):
    """Given a sequence of :class:`mkname.model.Name` objects with
    non-unique IDs, :func:`mkname.tools.redindex` should reindex the
    names to have unique ideas.
    """
    nonunique = [m.Name(0, *name.astuple()[1:]) for name in names]
    result = t.reindex(nonunique, offset=1)
    assert result == names


class TestWriteToCSV:
    def test_write_names(self, names, tmp_path):
        """When given a path and a sequence of names,
        :func:`mkname.tools.write_as_csv` should serialize
        the names as a CSV file.
        """
        path = tmp_path / 'names.csv'
        t.write_as_csv(path, names)
        with open(path) as fh:
            reader = csv.reader(fh)
            for row, name in zip(reader, names):
                assert m.Name(*row) == name

    def test_file_exists(self, names, tmp_path):
        """If the given path exists, :func:`mkname.tools.write_as_csv`
        should raise an exception.
        """
        path = tmp_path / 'names.csv'
        path.touch()
        with pytest.raises(t.PathExistsError):
            t.write_as_csv(path, names)

    def test_given_str(self, names, tmp_path):
        """When given a path as a str and a sequence of names,
        :func:`mkname.tools.write_as_csv` should serialize
        the names as a CSV file.
        """
        path = tmp_path / 'names.csv'
        t.write_as_csv(str(path), names)
        with open(path) as fh:
            reader = csv.reader(fh)
            for row, name in zip(reader, names):
                assert m.Name(*row) == name

    def test_overwrite_existing_file(self, names, tmp_path):
        """If override is `True`, :mod:`mkname.tools.write_as_csv`
        should overwrite the existing file.
        """
        path = tmp_path / 'names.csv'
        path.touch()
        t.write_as_csv(path, names, overwrite=True)
        with open(path) as fh:
            reader = csv.reader(fh)
            for row, name in zip(reader, names):
                assert m.Name(*row) == name
