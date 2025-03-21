"""
.. _tools_api:

#####
Tools
#####

This provides the API for creating custom :ref:`names databases <names_db>`.

.. note:
    Before writing code to create custom :ref:`names databases <names_db>`,
    take a look at the `mkname_tools` command line script to see if it
    will do what you need.


.. _cmd_scripts:

Command Scripts
---------------
The following are the core command scripts that automate the main
actions :mod:`mkname.tools` is intended to perform.

.. autofunction:: mkname.tools.add
.. autofunction:: mkname.tools.copy
.. autofunction:: mkname.tools.export
.. autofunction:: mkname.tools.import_
.. autofunction:: mkname.tools.new


.. _read_source:

Read Source Data
----------------
These functions can read common sources of name data for use in
a :ref:`name databases <names_db>`.

.. autofunction:: mkname.tools.read_csv
.. autofunction:: mkname.tools.read_name_census
.. autofunction:: mkname.tools.read_us_census


.. _write_data:

Write Data
----------
This function writes a :ref:`name databases <names_db>` out to a file
for editing.

.. autofunction:: mkname.tools.write_as_csv


.. _utility_tools:

Utility Functions
-----------------
This function manipulates names data in useful ways.

.. autofunction:: mkname.tools.reindex

"""
import csv
from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from mkname import db, init
from mkname import model as m
from mkname.constants import MSGS
from mkname.exceptions import *
from mkname.utility import recapitalize


# Names exported with *.
__all__ = [
    'add',
    'copy',
    'export',
    'INPUT_FORMATS',
    'import_',
    'new',
]

# Constants.
INPUT_FORMATS = ('csv', 'census.name', 'census.gov',)


# Public functions.
def read_csv(path: str | Path) -> tuple[m.Name, ...]:
    """Deserialize :class:`mkname.model.Name` objects serialized
    to a CSV file.

    :param path: The location of the file to read.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    rows = _get_rows_from_csv(path)
    return tuple(m.Name(*row) for row in rows)


def read_name_census(
    path: str | Path,
    source: str,
    year: int,
    kind: str,
    headers: bool = True
) -> tuple[m.Name, ...]:
    """Read a CSV file containing census.name formatted name data.

    :param path: The path to the CSV file.
    :param source: The URL for the data source.
    :param date: The year the data comes from.
    :param kind: A tag for how the name is used, such as a given
        name or a surname.
    :param headers: Whether the file has headers that need to be
        ignored. Defaults to `True`.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    rows = _get_rows_from_csv(path, delim=';')
    if headers:
        rows = rows[1:]
    return tuple(
        m.Name.from_name_census(row, source, year, kind, i)
        for i, row in enumerate(rows)
    )


def read_us_census(
    path: str | Path,
    source: str,
    culture: str = 'United States',
    year: int = 1970,
    gender: str = 'none',
    kind: str = 'surname',
    headers: bool = True
) -> tuple[m.Name, ...]:
    """Deserialize name data in U.S. Census name frequency data.

    :param path: The path to the TSV file.
    :param source: The URL for the data source.
    :param culture: The culture or nation the data is tied to.
    :param date: The approximate year the data is tied to.
    :param gender: The gender typically associated with the data
        during the time and in the culture the name is from.
    :param kind: A tag for how the data is used, such as a given
        name or a surname.
    :param headers: Whether the file has headers that need to be
        ignored. Defaults to `True`.
    :returns: A :class:`tuple` object.
    :rtype: tuple

    .. note:
        Since 2000, the U.S. Census Bureau puts this data in XLSX format.
        This function expects the data to be in tab separate value (TSV)
        format. To use this function, you will need to use some other
        application to convert the file from the U.S. Census Bureau from
        XLSX to TSV.
    """
    rows = _get_rows_from_csv(path, delim='\t')

    # If headers, find the first blank line then skip one.
    if headers:
        for i, row in enumerate(rows):
            if not row[0]:
                break
        else:
            i = 0
        rows = rows[i + 2:]

    # Convert the rows to Name objects and return.
    names = []
    for i, row in enumerate(rows):
        s = recapitalize(row[0])
        if not s:
            break
        name = m.Name(i, s, source, culture, year, gender, kind)
        names.append(name)
    return tuple(names)


def reindex(names: Sequence[m.Name], offset: int = 0) -> tuple[m.Name, ...]:
    """Reindex the given sequence of names.

    :param names: A sequence of names to reindex.
    :param offset: The first index when reindexing.
    :return: A :class:`tuple` object.
    :rtype: tuple
    """
    return tuple(
        m.Name(i + offset, *name.astuple()[1:])
        for i, name in enumerate(names)
    )


def write_as_csv(
    path: str | Path,
    names: Sequence[m.Name],
    overwrite: bool = False
) -> None:
    """Serialize the given :class:`mkname.model.Name` objects
    as a CSV file.

    :param path: Where to save the names.
    :param names: The names to save.
    :param overwrite: Whether to overwrite an existing file.
    :returns: `None`.
    :rtype: NoneType
    """
    path = Path(path)
    if path.exists() and not overwrite:
        msg = MSGS['en']['write_path_exists'].format(path=path)
        raise PathExistsError(msg)

    with open(path, 'w') as fh:
        writer = csv.writer(fh)
        for name in names:
            writer.writerow(name.astuple())


# Private functions.
def _get_rows_from_csv(
    path: str | Path,
    delim: str = ','
) -> tuple[tuple[str, ...], ...]:
    path = Path(path)
    if not path.exists():
        msg = MSGS['en']['read_path_not_exists'].format(path=path)
        raise PathDoesNotExistError(msg)

    with open(path) as fh:
        reader = csv.reader(fh, delimiter=delim)
        return tuple(tuple(row) for row in reader)


# Command scripts.
def add(
    dst_path: Path | str,
    name: str,
    source: str = 'unknown',
    culture: str = 'unknown',
    date: int = 1970,
    gender: str = 'unknown',
    kind: str = 'unknown'
) -> None:
    """Add a name to a names database.

    .. warning:
        This will not directly write to the default database. This
        is because updates to this package would overwrite any
        changes made by users to the default database. If you
        really want to do this anyway, you can still do it manually
        by writing out to a copy of the default database and then
        copying that copy over the default database.

    :param dst_path: The database destination for the new name.
    :param name: The name.
    :param source: The URL where the name was found.
    :param culture: The culture or nation the name is tied to.
    :param date: The approximate year the name is tied to.
    :param gender: The gender typically associated with the name
        during the time and in the culture the name is from.
    :param kind: A tag for how the name is used, such as a given
        name or a surname.
    :returns: `None`.
    :rtype: NoneType
    """
    # Protect the default database.
    dst_path = Path(dst_path)
    default_db = init.get_default_db()
    if dst_path == default_db:
        raise DefaultDatabaseWriteError(MSGS['en']['default_db_write'])

    # Add the name to the database.
    id_ = db.get_max_id(dst_path) + 1
    new = m.Name(
        id=id_,
        name=name,
        source=source,
        culture=culture,
        date=date,
        gender=gender,
        kind=kind
    )
    db.add_name_to_db(dst_path, new)


def copy(dst_path: Path | str | None) -> Path:
    """Copy a names database to a new location.

    :param dst_path: The destination of the copy.
    :returns: A :class:`pathlib.Path` object.
    :rtype: pathlib.Path
    """
    # Determine the destination path for the copy.
    dst_path = Path(dst_path) if dst_path else Path('names.db')
    if dst_path.is_dir():
        dst_path = dst_path / 'names.db'

    # Do not overwrite existing files.
    if dst_path.exists():
        msg = MSGS['en']['dup_path_exists'].format(dst_path=dst_path)
        raise PathExistsError(msg)

    # Copy the default database.
    db.duplicate_db(dst_path)
    return dst_path


def export(
    dst_path: Path | str,
    src_path: Path | str | None = None,
    cfg_path: Path | str | None = None,
    overwrite: bool = False
) -> None:
    """Export names databases to CSV files for manual updating.

    :param dst_path: The CSV destination for the export.
    :param src_path: (Optional.) The database source of the
        data to export. Defaults to the default database.
    :param overwrite: (Optional.) Whether to overwrite an existing
        destination path. Defaults to `False`.
    """
    db_path = init.get_db(src_path, conf_path=cfg_path)
    names = db.get_names(db_path)
    write_as_csv(dst_path, names, overwrite=overwrite)


def import_(
    dst_path: Path | str,
    src_path: Path | str,
    format: str = 'csv',
    source: str = 'unknown',
    date: int = 1970,
    kind: str = 'unknown',
    update: bool = False
) -> None:
    """Import names from a file to a database.

    .. warning:
        This will not directly write to the default database. This
        is because updates to this package would overwrite any
        changes made by users to the default database. If you
        really want to do this anyway, you can still do it manually
        by writing out to a copy of the default database and then
        copying that copy over the default database.

    :param dst_path: The database destination for the import.
    :param src_path: The source of the name data to import.
    :param format: The format of the source data. Valid options
        are `csv`, `census.name`, and `census.gov`.
    :param source: (Optional.) Where the source data comes from.
        Defaults to `unknown`. This is used only for formats that
        need it.
    :param date: (Optional.) The approximate year for the imported
        data. Defaults to `1970`. This is used only for formats that
        need it.
    :param kind: (Optional.) The kind of name in the imported data.
        Defaults to `unknown`. This is used only for formats that
        need it.
    :param update: (Optional.) Whether to update records with
        colliding IDs or throw an error. Defaults to False, which
        throws the error.
    :returns: `None`.
    :rtype: NoneType
    """
    dst_path = Path(dst_path)
    default_db = init.get_default_db()
    if dst_path == default_db:
        raise DefaultDatabaseWriteError(MSGS['en']['default_db_write'])

    if format == 'csv':
        names = read_csv(src_path)
    elif format == 'census.name':
        names = read_name_census(src_path, source, date, kind)
    elif format == 'census.gov':
        names = read_us_census(src_path, source, year=date, kind=kind)
    else:
        msg = MSGS['en']['invalid_format'].format(format=format)
        raise InvalidImportFormatError(msg)
    if not dst_path.exists():
        db.create_empty_db(dst_path)

    i = db.get_max_id(dst_path)
    if i and not update:
        names = reindex(names, offset=i + 1)
    db.add_names_to_db(dst_path, names, update=update)


def new(dst_path: Path | str | None = None) -> Path:
    """Create an empty names database.

    :param dst_path: The database destination for the import.
    :returns: A :class:`pathlib.Path` object.
    :rtype: pathlib.Path
    """
    # Determine the path for the database.
    dst_path = Path(dst_path) if dst_path else Path('names.db')
    if dst_path.is_dir():
        dst_path = dst_path / 'names.db'

    # Do not overwrite existing files.
    if dst_path.exists():
        msg = MSGS['en']['new_path_exists'].format(dst_path=dst_path)
        raise PathExistsError(msg)

    # Create the new database.
    db.create_empty_db(dst_path)
    return dst_path
