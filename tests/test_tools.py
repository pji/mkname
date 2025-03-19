"""
test_tools
~~~~~~~~~~

Unit tests for :mod:`mkname.tools`.
"""
import pytest

import mkname.model as m
import mkname.tools as t
from tests.common import csv_matches_names, db_matches_names
from tests.fixtures import *


# Test cases.
class TestAdd:
    def test_add(self, name, names, tmp_db):
        """Given the path to a database and name data,
        :func:`mkname.tools.add` should add that name to
        the database.
        """
        t.add(
            dst_path=tmp_db,
            name=name.name,
            source=name.source,
            culture=name.culture,
            date=name.date,
            gender=name.gender,
            kind=name.kind
        )
        assert db_matches_names(tmp_db, [*names, name])

    def test_cannot_write_to_default(self, name, names, prot_db):
        """If you try to add a name to the default db,
        :func:`mkname.tools.add` will raise a
        :class:`mkname.tools.DefaultDatabaseWriteError`
        exception.
        """
        with pytest.raises(t.DefaultDatabaseWriteError):
            t.add(
                dst_path=prot_db,
                name=name.name,
                source=name.source,
                culture=name.culture,
                date=name.date,
                gender=name.gender,
                kind=name.kind
            )
        assert db_matches_names(prot_db, names)


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
        assert csv_matches_names(path, names)

    def test_export_default_db(self, names, test_db, tmp_path):
        """Given a path, :func:`mkname.tools.export` should export
        the names in the default names database to a CSV file at
        the path.
        """
        path = tmp_path / 'names.csv'
        assert not path.exists()
        t.export(path)
        assert csv_matches_names(path, names)

    def test_export_given_db(self, db_path, names, tmp_path):
        """Given a destination and a source path,
        :func:`mkname.tools.export` should export the
        names in the source names database to a CSV
        file at the destination path.
        """
        dst_path = tmp_path / 'names.csv'
        assert not dst_path.exists()
        t.export(dst_path, src_path=db_path)
        assert csv_matches_names(dst_path, names)

    def test_export_configured_db(self, conf_full_path, names, tmp_path):
        """Given a destination and a config file with
        a configured database,:func:`mkname.tools.export`
        should export the names in the source names
        database to a CSV file at the destination path.
        """
        dst_path = tmp_path / 'names.csv'
        assert not dst_path.exists()
        t.export(dst_path, cfg_path=conf_full_path)
        assert csv_matches_names(dst_path, names)

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
    def test_census_name_given_names(
        self, census_name_given_names,
        census_name_given_path,
        empty_db
    ):
        """Given a path to an existing name database, a path to
        an existing file of given name data in census.name format,
        :func:`mkname.tools.import_` should add the names in the
        census.name file to the database.
        """
        format = 'census.name'
        source = 'census.name'
        date = 2025
        kind = 'given'
        t.import_(
            dst_path=empty_db,
            src_path=census_name_given_path,
            format=format,
            source=source,
            date=date,
            kind=kind
        )
        assert db_matches_names(empty_db, census_name_given_names)

    def test_import_into_existing(self, csv_path, empty_db, names):
        """Given a path to an existing names database and a path to
        an existing CSV file of name data, :func:`mkname.tools.import`
        should add the names in the CSV to the database.
        """
        t.import_(empty_db, csv_path)
        assert db_matches_names(empty_db, names)

    def test_import_into_exisiting_with_changes(
        self, csv_path, change_db, names
    ):
        """Given a path to an existing names database, a path to
        an existing CSV file of name data, and the update option,
        :func:`mkname.tools.import` should add the names in the CSV
        to the database, updating any names with IDs that exist in
        the database and CSV.
        """
        t.import_(change_db, csv_path, update=True)
        assert db_matches_names(change_db, names)

    def test_import_into_nonexisting(self, csv_path, names, tmp_path):
        """Given a path to a nonexisting names database and a path to
        an existing CSV file of name data, :func:`mkname.tools.import`
        should add the names in the CSV to the database.
        """
        path = tmp_path / 'names.db'
        t.import_(path, csv_path)
        assert db_matches_names(path, names)

    def test_invalid_format(self):
        """If given an invalid format value, :func:`makname.tools.import_`
        should raise a `InvvalidImportFormatError` exception.
        """
        dst_path = 'spam'
        src_path = 'eggs'
        format = 'bacon'
        with pytest.raises(t.InvalidImportFormatError):
            t.import_(dst_path, src_path, format)

    def test_us_census_surnames(
        self, empty_db,
        census_gov_surnames_names,
        census_gov_surnames_path
    ):
        """Given a path to an existing name database, a path to
        an existing file of given name data in census.gov format,
        :func:`mkname.tools.import_` should add the names in the
        census.gov file to the database.
        """
        format = 'census.gov'
        source = 'census.gov'
        date = 2010
        kind = 'surname'
        t.import_(
            dst_path=empty_db,
            src_path=census_gov_surnames_path,
            format=format,
            source=source,
            date=date,
            kind=kind
        )
        assert db_matches_names(empty_db, census_gov_surnames_names)

    def test_will_reindex_unique_ids(
        self, census_name_given_names,
        census_name_given_path,
        names,
        tmp_db
    ):
        """Given names with unique IDs that match names already in
        the database, :func:`mkname.tools.import_` should reindex
        the new names to ensure there are no collisions.
        """
        expected = []
        expected.extend(names)
        for name in census_name_given_names:
            reindexed = m.Name(len(expected) + 1, *name.astuple()[1:])
            expected.append(reindexed)

        format = 'census.name'
        source = 'census.name'
        date = 2025
        kind = 'given'
        t.import_(
            dst_path=tmp_db,
            src_path=census_name_given_path,
            format=format,
            source=source,
            date=date,
            kind=kind
        )
        assert db_matches_names(tmp_db, expected)


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
    def test_read_given_names(
        self, census_name_given_names,
        census_name_given_path
    ):
        """Given a path to a file containing given name data
        stored in census.name format, a source, a year, and
        a kind, :func:`mkname.tools.read_name_census` should
        return the names in the file as a :class:`tuple`
        of :class:`mkname.model.Name` objects.
        """
        path = census_name_given_path
        year = 2025
        kind = 'given'
        source = 'census.name'
        result = t.read_name_census(path, source, year, kind)
        for actual, expected in zip(result, census_name_given_names):
            assert actual == expected

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
    def test_surname_2010(
        self, census_gov_surnames_names,
        census_gov_surnames_path
    ):
        """Given the path to a TSV file in U.S. Census 2010 Surname
        format, a source, a year, a gender, a kind, and whether there
        are headers, :func:`mkname.tools.read_us_census` should read
        the file and return a :class:`tuple` object of
        class:`mkname.model.Name` objects.
        """
        source = 'census.gov'
        kind = 'surname'
        year = 2010
        headers = True
        result = t.read_us_census(
            census_gov_surnames_path,
            source=source,
            year=year,
            kind=kind,
            headers=headers
        )
        assert result == census_gov_surnames_names


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
        assert csv_matches_names(path, names)

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
        assert csv_matches_names(path, names)

    def test_overwrite_existing_file(self, names, tmp_path):
        """If override is `True`, :mod:`mkname.tools.write_as_csv`
        should overwrite the existing file.
        """
        path = tmp_path / 'names.csv'
        path.touch()
        t.write_as_csv(path, names, overwrite=True)
        assert csv_matches_names(path, names)
