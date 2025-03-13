"""
tools
~~~~~

Tools for working with alternate sources of name data.

.. autofunction:: mkname.tools.read_csv
.. autofunction:: mkname.tools.read_name_census
.. autofunction:: mkname.tools.read_us_census
.. autofunction:: mkname.tools.reindex
.. autofunction:: mkname.tools.write_as_csv


Command Scripts
===============
The following are the core command scripts that allow easy use of
:mod:`mkname.tools` from the command line.

.. autofunction:: mkname.tools.import_
.. autofunction:: mkname.tools.export

"""
import csv
from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from mkname import db, init
from mkname import model as m
from mkname.constants import MSGS
from mkname.utility import recapitalize


# Exceptions.
class DefaultDatabaseWriteError(IOError):
    """There was an attempt to write directly to the default database.
    This is prevented because updates to this package would overwrite
    any changes to the default database, causing confusion.
    """


class InvalidImportFormatError(ValueError):
    """The format assigned to the file to be imported was not a
    format that :mod:`mkname` knows how to format.
    """


class PathDoesNotExistError(FileNotFoundError):
    """Raised when a path unexpectedly doesn't exist. This is usually
    used to handle requests to read from non-existing files.
    """


class PathExistsError(IOError):
    """Raised when a path exists unexpectedly. This is usually used to
    prevent overwriting existing files when writing data.
    """


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
def export(
    dst_path: Path | str,
    src_path: Path | str | None = None,
    overwrite: bool = False
) -> None:
    """Export names databases to CSV files for manual updating.

    :param dst_path: The CSV destination for the export.
    :param src_path: (Optional.) The database source of the
        data to export. Defaults to the default database.
    :param overwrite: (Optional.) Whether to overwrite an existing
        destination path. Defaults to `False`.
    """
    names = db.get_names(src_path)
    write_as_csv(dst_path, names, overwrite=overwrite)


def import_(
    dst_path: Path | str,
    src_path: Path | str,
    format: str = 'csv',
    source: str = 'unknown',
    date: int = 1970,
    kind: str = 'unknown'
) -> None:
    """Import names from a file to a database.

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
    if i:
        names = reindex(names, offset=i + 1)
    db.add_names_to_db(dst_path, names)
