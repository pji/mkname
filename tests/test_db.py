"""
test_db
~~~~~~~

Unit tests for the mkname.db module.
"""
import pathlib
import sqlite3

import pytest

from mkname import db
from mkname import model as m
from mkname.exceptions import DefaultDatabaseWriteError
from tests.common import db_matches_names
from tests.fixtures import *


# Fixtures
@pytest.fixture
def con():
    """Manage a test database connection."""
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    yield con
    con.close()


# Connection test cases.
def test_connect():
    """When given the path to an sqlite3 database, db.connect_db
    should return a connection to the database.
    """
    # Test data and state.
    db_path = 'tests/data/names.db'
    query = 'select name from names where id = 1;'

    # Run test.
    con = db.connect_db(db_path)
    try:
        selected = con.execute(query)
        result = selected.fetchone()
    finally:
        con.close()

    # Determine test result.
    assert result == ('spam',)


def test_connect_no_file():
    """If the given file does not exist, db.connect_db should raise
    a ValueError.
    """
    # Test data and state.
    db_path = 'tests/data/no_file.db'
    path = pathlib.Path(db_path)
    if path.is_file():
        msg = f'Remove file at "{path}".'
        raise RuntimeError(msg)

    # Run test and determine results.
    with pytest.raises(ValueError, match=f'No database at "{path}".'):
        _ = db.connect_db(path)


def test_disconnect():
    """When given a database connection, close it."""
    # Test data and state.
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    query = 'select name from names where id = 1;'
    result = None

    # Run test.
    db.disconnect_db(con)

    # Determine test result
    with pytest.raises(
        sqlite3.ProgrammingError,
        match='Cannot operate on a closed database.'
    ):
        result = con.execute(query)

    # Clean up test.
    if result:
        con.close()


def test_disconnect_with_pending_changes():
    """When given a database connection, raise an exception if
    the connection contains uncommitted changes instead of closing
    the connection.
    """
    # Test data and state.
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    query = "insert into names values (null, 'test', '', '', 0, '', '')"
    _ = con.execute(query)
    result = None

    # Run test and determine result.
    with pytest.raises(
        RuntimeError,
        match='Connection has uncommitted changes.'
    ):
        db.disconnect_db(con)


# Read test cases.
class DeserializationTest:
    fn = None
    exp = None

    def test_with_connection(self, con):
        """Given a connection, the function should return the
        expected response.
        """
        fn = getattr(db, self.fn)
        assert fn(con) == self.exp

    def test_with_path(self, db_path):
        """Given a path to a database, the function should return the
        expected response.
        """
        fn = getattr(db, self.fn)
        assert fn(db_path) == self.exp

    def test_without_connection_or_path(self, test_db):
        """Given neither a path  or a connection to a database, the
        function should return the expected response.
        """
        fn = getattr(db, self.fn)
        assert fn() == self.exp


class TestGetCultures(DeserializationTest):
    fn = 'get_cultures'
    exp = ('bacon', 'pancakes', 'porridge',)


class TestGetDates(DeserializationTest):
    fn = 'get_dates'
    exp = (1970, 2000,)


class TestGetGenders(DeserializationTest):
    fn = 'get_genders'
    exp = ('sausage', 'baked beans')


class TestGetKinds(DeserializationTest):
    fn = 'get_kinds'
    exp = ('given', 'surname',)


class TestGetSources(DeserializationTest):
    fn = 'get_sources'
    exp = ('eggs', 'mushrooms',)


def test_get_names(con, names):
    """When given a database connection, :func:`mkname.db.get_names`
    should return the names in the given database as a tuple.
    """
    # Expected value.
    assert db.get_names(con) == names


@pytest.mark.dependency()
def test_get_names_called_with_path(db_path, names):
    """When called with a path to a database, :func:`mkname.db.get_name`
    should return the names in the given database as a tuple.
    """
    assert db.get_names(db_path) == names


def test_get_names_called_without_connection_or_path(test_db, names):
    """When called without a connection, :func:`mknames.db.get_names`
    should return the names in the default database as a tuple.
    """
    assert db.get_names() == names


@pytest.mark.skip
def test_get_names_by_kind(con):
    """When given a database connection and a kind,
    :func:`mkname.db.get_names_by_kind` should return the
    names of that kind in the given database as a tuple.
    """
    # Expected value.
    kind = 'surname'
    assert db.get_names_by_kind(con, kind) == (
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
    )


@pytest.mark.skip
def test_get_names_by_kind_with_path():
    """When given a path and a kind, :func:`mkname.db.get_names_by_kind`
    should return the names of that kind in the given database as a tuple.
    """
    # Expected value.
    db_path = 'tests/data/names.db'
    kind = 'surname'
    assert db.get_names_by_kind(db_path, kind) == (
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
    )


@pytest.mark.skip
def test_get_names_by_kind_without_connection_or_path(test_db):
    """When given a kind, :func:`mkname.db.get_names_by_kind`
    should return the names of that kind in the default database
    as a tuple.
    """
    # Expected value.
    kind = 'surname'
    assert db.get_names_by_kind(kind=kind) == (
        m.Name(
            3,
            'tomato',
            'mushrooms',
            'pancakes',
            2000,
            'sausage',
            'surname'
        ),
    )


# Create test cases.
class TestAdminActions:
    def test_create_db(self, names, tmp_path):
        """Given a path, :func:`mkname.db.create_empty_db` should
        create an empty copy of the names database at that location.
        """
        name = names[0]
        path = tmp_path / 'names.db'
        assert not path.exists()
        db.create_empty_db(path)
        con = sqlite3.Connection(path)
        con.execute(
            (
                'INSERT INTO names '
                'VALUES(:id, :name, :src, :culture, :date, :gender, :kind)'
            ),
            {
                'id': name.id,
                'name': name.name,
                'src': name.source,
                'culture': name.culture,
                'date': name.date,
                'gender': name.gender,
                'kind': name.kind,
            }
        )

    @pytest.mark.dependency(depends=['test_get_names_called_with_path'],)
    def test_duplicate_db(self, test_db, names, tmp_path):
        """When given a destination path, :func:`mkname.db.duplicate_db`
        should create a copy of the names DB in the current working directory.
        """
        dst_path = tmp_path / 'names.db'
        db.duplicate_db(dst_path)
        assert dst_path.exists()
        assert db.get_names(dst_path) == names

    @pytest.mark.dependency(depends=['test_get_names_called_with_path'],)
    def test_duplicate_db_with_str(self, test_db, names, tmp_path):
        """When given a destination path, :func:`mkname.db.duplicate_db`
        should create a copy of the names DB in the current working directory.
        """
        dst_str = str(tmp_path / 'names.db')
        db.duplicate_db(dst_str)
        assert pathlib.Path(dst_str).exists()
        assert db.get_names(dst_str) == names


class TestCreateActions:
    def test_add_name_to_db(self, empty_db, names):
        """Given a name and a path to a names database,
        :func:`mkname.db.add_name_to_db` should add the name
        to the database.
        """
        name = names[0]
        db.add_name_to_db(empty_db, name)
        con = sqlite3.Connection(empty_db)
        cur = con.cursor()
        result = cur.execute('SELECT * FROM names WHERE id=1;')
        assert result.fetchone()[1] == name.name

    def test_add_name_to_db_cannot_update_default_db(
        self, prot_db, names
    ):
        """When given `None` instead of a database connection or path,
        :func:`mkname.db.add_name_to_db` should raise an exception to
        prevent accidental changes to the default database.
        """
        with pytest.raises(DefaultDatabaseWriteError) as e_info:
            db.add_name_to_db(None, names[0])

    def test_add_names_to_db(self, empty_db, names):
        """Given a sequence of names and a path to a names database,
        :func:`mkname.db.add_names_to_db` should add the names
        to the database.
        """
        db.add_names_to_db(empty_db, names)
        con = sqlite3.Connection(empty_db)
        cur = con.cursor()
        result = cur.execute('SELECT * FROM names;')
        actuals = result.fetchall()
        for act, exp in zip(actuals, names):
            assert act[1] == exp.name

    def test_add_names_to_db_cannot_update_default_db(
        self, prot_db, names
    ):
        """When given `None` instead of a database connection or path,
        :func:`mkname.db.add_name_to_db` should raise an exception to
        prevent accidental changes to the default database.
        """
        with pytest.raises(DefaultDatabaseWriteError) as e_info:
            db.add_names_to_db(None, names)

    def test_add_names_to_db_with_updates(self, change_db, names):
        """Given a sequence of names, a path to a names database,
        and update `True`, :func:`mkname.db.add_names_to_db` should
        add the names to the database and update any records with
        IDs that conflict with the new names to the values of the
        new name.
        """
        db.add_names_to_db(change_db, names, update=True)
        assert db_matches_names(change_db, names)
