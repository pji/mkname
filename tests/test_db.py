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


# Fixtures
@pytest.fixture
def con():
    """Manage a test database connection."""
    db_path = 'tests/data/names.db'
    con = sqlite3.Connection(db_path)
    yield con
    con.close()


@pytest.fixture
def db_path():
    return 'tests/data/names.db'


@pytest.fixture
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


@pytest.fixture
def protected_test_db(mocker, tmp_path):
    """Point the default database to the temp copy of the test database."""
    test_db_path = pathlib.Path('tests/data/names.db')
    db_path = pathlib.Path(tmp_path / 'names.db')
    data = test_db_path.read_bytes()
    db_path.write_bytes(data)
    path_str = str(db_path)
    mocker.patch('mkname.db.get_db', return_value=path_str)
    yield None


@pytest.fixture
def test_db(mocker, tmp_path):
    """Point the default database to the test database."""
    db_path = 'tests/data/names.db'
    mocker.patch('mkname.db.get_db', return_value=db_path)
    yield None


@pytest.fixture
def test_names():
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


class TestGetGenders(DeserializationTest):
    fn = 'get_genders'
    exp = ('sausage', 'baked beans')


class TestGetKinds(DeserializationTest):
    fn = 'get_kinds'
    exp = ('given', 'surname',)


def test_get_names(con, test_names):
    """When given a database connection, :func:`mkname.db.get_names`
    should return the names in the given database as a tuple.
    """
    # Expected value.
    assert db.get_names(con) == test_names


@pytest.mark.dependency()
def test_get_names_called_with_path(db_path, test_names):
    """When called with a path to a database, :func:`mkname.db.get_name`
    should return the names in the given database as a tuple.
    """
    assert db.get_names(db_path) == test_names


def test_get_names_called_without_connection_or_path(test_db, test_names):
    """When called without a connection, :func:`mknames.db.get_names`
    should return the names in the default database as a tuple.
    """
    assert db.get_names() == test_names


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
@pytest.mark.dependency(depends=['test_get_names_called_with_path'],)
def test_duplicate_db(test_db, test_names, tmp_path):
    """When given a destination path, :func:`mkname.db.duplicate_db`
    should create a copy of the names DB in the current working directory.
    """
    dst_path = tmp_path / 'names.db'
    db.duplicate_db(dst_path)
    assert dst_path.exists()
    assert db.get_names(dst_path) == test_names


@pytest.mark.dependency(depends=['test_get_names_called_with_path'],)
def test_duplicate_db_with_str(test_db, test_names, tmp_path):
    """When given a destination path, :func:`mkname.db.duplicate_db`
    should create a copy of the names DB in the current working directory.
    """
    dst_str = str(tmp_path / 'names.db')
    db.duplicate_db(dst_str)
    assert pathlib.Path(dst_str).exists()
    assert db.get_names(dst_str) == test_names


# Update test cases.
def test_add_name_to_db(empty_db, test_names):
    """Given a name and a path to a names database,
    :func:`mkname.db.add_name_to_db` should add the name
    to the database.
    """
    name = test_names[0]
    db.add_name_to_db(empty_db, name)
    con = sqlite3.Connection(empty_db)
    cur = con.cursor()
    result = cur.execute('SELECT * FROM names WHERE id=1;')
    assert result.fetchone()[1] == name.name


def test_add_name_to_db_cannot_update_default_db(
    protected_test_db,
    test_names
):
    """When given `None` instead of a database connection or path,
    :func:`mkname.db.add_name_to_db` should raise an exception to
    prevent accidental changes to the default database.
    """
    with pytest.raises(db.CannotUpdateDefaultDBError) as e_info:
        db.add_name_to_db(None, test_names[0])


def test_add_names_to_db(empty_db, test_names):
    """Given a sequence of names and a path to a names database,
    :func:`mkname.db.add_names_to_db` should add the names
    to the database.
    """
    db.add_names_to_db(empty_db, test_names)
    con = sqlite3.Connection(empty_db)
    cur = con.cursor()
    result = cur.execute('SELECT * FROM names;')
    actuals = result.fetchall()
    for act, exp in zip(actuals, test_names):
        assert act[1] == exp.name


def test_add_names_to_db_cannot_update_default_db(
    protected_test_db,
    test_names
):
    """When given `None` instead of a database connection or path,
    :func:`mkname.db.add_name_to_db` should raise an exception to
    prevent accidental changes to the default database.
    """
    with pytest.raises(db.CannotUpdateDefaultDBError) as e_info:
        db.add_names_to_db(None, test_names)
