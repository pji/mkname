"""
test_tools
~~~~~~~~~~

Unit tests for :mod:`mkname.tools`.
"""
import csv
import sqlite3

import pytest

import mkname.model as m
import mkname.tools as t
from tests.fixtures import csv_path, db_path, empty_db, names, test_db


# Utility functions.
def db_matches_names(path, names):
    """Compare the names in the DB to the given names."""
    query = 'SELECT * FROM names'
    con = sqlite3.Connection(path)
    rows = con.execute(query)
    results = [m.Name(*row) == name for row, name in zip(rows, names)]
    con.close()
    return results


def csv_matches_names(path, names):
    """Compare the names in the CSV file to the given names."""
    with open(path) as fh:
        reader = csv.reader(fh)
        results = [m.Name(*row) == name for row, name in zip(reader, names)]
    return results


# Test cases.
class TestExport:
    def test_can_overwrite(self, names, test_db, tmp_path):
        """Given a destination path that exists and a `overwrite`
        value of `True`, :func:`mkname.tools.export` should overwrite
        the path.
        """
        path = tmp_path / 'names.csv'
        path.touch()
        assert path.exists()
        t.export(path, overwrite=True)
        assert all(csv_matches_names(path, names))

    def test_export_default_db(self, names, test_db, tmp_path):
        """Given a path, :func:`mkname.tools.export` should export
        the names in the default names database to a CSV file at
        the path.
        """
        path = tmp_path / 'names.csv'
        assert not path.exists()
        t.export(path)
        assert all(csv_matches_names(path, names))

    def test_export_given_db(self, db_path, names, tmp_path):
        """Given a destination and a source path,
        :func:`mkname.tools.export` should export the
        names in the source names database to a CSV
        file at the destination path.
        """
        dst_path = tmp_path / 'names.csv'
        assert not dst_path.exists()
        t.export(dst_path, src_path=db_path)
        assert all(csv_matches_names(dst_path, names))

    def test_will_not_overwrite(self, tmp_path):
        """Given a destination path that exists,
        :func:`mkname.tools.export` should raise
        an exception rather than overwrite the
        file at the path.
        """
        dst_path = tmp_path / 'spam'
        dst_path.touch()
        assert dst_path.exists()
        with pytest.raises(t.PathExistsError):
            t.export(dst_path)


class TestImport_:
    def test_import_into_existing(self, csv_path, empty_db, names):
        """Given a path to an existing names database and a path to
        an existing CSV file of name data, :func:`mkname.tools.import`
        should add the names in the CSV to the database.
        """
        t.import_(empty_db, csv_path)
        assert all(db_matches_names(empty_db, names))

    def test_import_into_nonexisting(self, csv_path, names, tmp_path):
        """Given a path to a nonexisting names database and a path to
        an existing CSV file of name data, :func:`mkname.tools.import`
        should add the names in the CSV to the database.
        """
        path = tmp_path / 'names.db'
        t.import_(path, csv_path)
        assert all(db_matches_names(path, names))


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


class TestReadNameCensus:
    def test_read_given_names(self):
        """Given a path to a file containing given name data
        stored in census.name format, a source, a year, and
        a kind, :func:`mkname.tools.read_name_census` should
        return the names in the file as a :class:`tuple`
        of :class:`mkname.model.Name` objects.
        """
        path = 'tests/data/census_name.csv'
        year = 2025
        kind = 'given'
        source = 'http://census.name'
        result = t.read_name_census(path, source, year, kind)
        assert len(result) == 5
        assert result[0] == m.Name(
            0, 'Сергей', source, 'Russia', year, 'male', kind
        )
        assert result[-1] == m.Name(
            4, 'Hélène', source, 'France', year, 'female', kind
        )

    def test_read_surnames(self):
        """Given a path to a file containing surname data
        stored in census.name format, a source, a year,
        and a kind, :func:`mkname.tools.read_name_census`
        should return the names in the file as a :class:`tuple`
        of :class:`mkname.model.Name` objects.
        """
        path = 'tests/data/census_name_surname.csv'
        year = 2025
        kind = 'surname'
        source = 'http://census.name'
        result = t.read_name_census(path, source, year, kind)
        assert len(result) == 6
        assert result[0] == m.Name(
            0, 'Nuñez', source, 'Spain', year, 'none', kind
        )
        assert result[-1] == m.Name(
            5, 'иванова', source, 'Russia', year, 'female', kind
        )


class TestReadUSCensus:
    def test_surname_2010(self):
        """Given the path to a TSV file in U.S. Census 2010 Surname
        format, a source, a year, a gender, a kind, and whether there
        are headers, :func:`mkname.tools.read_us_census` should read
        the file and return a :class:`tuple` object of
        class:`mkname.model.Name` objects.
        """
        path = 'tests/data/us_census_surnames.tsv'
        source = 'census.gov'
        kind = 'surname'
        year = 2025
        headers = True
        result = t.read_us_census(
            path,
            source=source,
            year=year,
            kind=kind,
            headers=headers
        )
        assert len(result) == 5
        assert result[0] == m.Name(
            id=0,
            name='Smith',
            source=source,
            culture='United States',
            date=year,
            gender='none',
            kind=kind
        )
        assert result[-1] == m.Name(
            id=4,
            name='Jones',
            source=source,
            culture='United States',
            date=year,
            gender='none',
            kind=kind
        )


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
        assert all(csv_matches_names(path, names))

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
        assert all(csv_matches_names(path, names))

    def test_overwrite_existing_file(self, names, tmp_path):
        """If override is `True`, :mod:`mkname.tools.write_as_csv`
        should overwrite the existing file.
        """
        path = tmp_path / 'names.csv'
        path.touch()
        t.write_as_csv(path, names, overwrite=True)
        assert all(csv_matches_names(path, names))
