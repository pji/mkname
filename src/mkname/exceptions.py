"""

.. _exceptions:

##########
Exceptions
##########

The following are the exceptions that can be raised by :mod:`mkname`.

.. autoclass:: mkname.ConfigFileDoesNotExistError
.. autoclass:: mkname.DefaultDatabaseWriteError
.. autoclass:: mkname.IDCollisionError
.. autoclass:: mkname.InvalidImportFormatError
.. autoclass:: mkname.PathDoesNotExistError
.. autoclass:: mkname.PathExistsError
.. autoclass:: mkname.StrExceedsUpperBound
.. autoclass:: mkname.UnsupportedPythonVersionError

"""

__all__ = [
    'ConfigFileDoesNotExistError',
    'DefaultDatabaseWriteError',
    'IDCollisionError',
    'InvalidImportFormatError',
    'NotADatabaseError',
    'PathDoesNotExistError',
    'PathExistsError',
    'StrExceedsUpperBound',
    'UnsupportedPythonVersionError',
]


# Exceptions.
class ConfigFileDoesNotExistError(FileNotFoundError):
    """The given configuration file does not exist."""


class DefaultDatabaseWriteError(RuntimeError):
    """There was an attempt to write directly to the default database.
    This is prevented because updates to this package would overwrite
    any changes to the default database, causing confusion.
    """


class IDCollisionError(ValueError):
    """The ID of the Name you tried to add to the database matches
    the ID of a name already in the database.
    """


class InvalidImportFormatError(ValueError):
    """The format assigned to the file to be imported was not a
    format that :mod:`mkname` knows how to format.
    """


class NotADatabaseError(FileNotFoundError):
    """The path that should have been a names database is not
    a names database.
    """


class PathDoesNotExistError(FileNotFoundError):
    """Raised when a path unexpectedly doesn't exist. This is usually
    used to handle requests to read from non-existing files.
    """


class PathExistsError(FileExistsError):
    """Raised when a path exists unexpectedly. This is usually used to
    prevent overwriting existing files when writing data.
    """


class StrExceedsUpperBound(ValueError):
    """The given :class:`str` is too large for the field."""


class UnsupportedPythonVersionError(RuntimeError):
    """The Python version doesn't support this action."""
