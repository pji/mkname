"""
tools
~~~~~

Tools for working with alternate sources of name data.
"""
import csv
from collections.abc import Sequence
from pathlib import Path

from mkname import model as m
from mkname.constants import MSGS


# Exceptions.
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
    path = Path(path)
    if not path.exists():
        msg = MSGS['en']['read_path_not_exists'].format(path=path)
        raise PathDoesNotExistError(msg)

    with open(path) as fh:
        reader = csv.reader(fh)
        return tuple(m.Name(*row) for row in reader)


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
