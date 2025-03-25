.. _config:

#############
Configuration
#############

Configuration of :mod:`mkname` is handled by configuration files.
Two formats are supported:

*   INI-like syntax supported by :mod:`configparser`,
*   `TOML`_ (requires Python 3.11 or higher).

.. _TOML: https://toml.io

The following describes the configuration file and how :mod:`mkname`
loads the configuration.


.. _config_files:

Configuration File Structure
============================
As mentioned above, configuration files need to be in INI-like format
or, if you are running Python 3.11 or higher, TOML format. The two
formats are very similar, so the examples will be in TOML format.
Just remember that if you use INI-like format instead, the string
values are not quoted in INI-like format.

.. note:
    Why doesn't :mod:`mkname` support TOML under Python 3.10?
    The standard library module I'm using to parse TOML,
    :mod:`tomllib` was only added to Python in 3.11. I could
    probably work around this for Python 3.10, but it seems
    like it would be more work than it's worth.

An example of the contents of a :mod:`mkname` configuration file::

    [mkname]
    consonants = "bcdfghjklmnpqrstvwxz"
    db_path =
    punctuation = "'-.?!/:@+|•"
    scifi_letters = "kqxz"
    vowels = "aeiouy"

The following is true of a :mod:`mkname` configuration file:

*   It must have a `[mkname]` section.
*   It may have any of the following keys:

    *   :ref:`consonants`,
    *   :ref:`db_path`,
    *   :ref:`punctuation`,
    *   :ref:`scifi_letters`,
    *   :ref:`vowels`.

*   No keys are required.

The keys are defined as follows.


.. _consonants:

consonants
----------
This defines the characters used as "consonants" by :mod:`mkname`. This
setting is primarily used to split names into syllables when generating
new names from multiple names from the database. The default value is
the standard list of English consonants, minus the letter `y`.


.. _db_path:

db_path
-------
This sets the names database used by :mod:`mkname`. It can be used to
have :mod:`mkname` use a custom names database rather than the default
names database. The default value is an empty string, which causes
:mod:`mkname` to go to the next step in the database search order.


.. _punctuation:

punctuation
-----------
This defines the characters used as punctuation marks by :mod:`mkname`.
This is primarily intended for use by :func:`mkname.mod.add_punctuation`
when modifying names to add punctuation marks. The default values are
listed in the example `mkname` section above.


.. _scifi_letters:

scifi_letters
-------------
The defines the characters used as "scifi letters" by :mod:`mkname`.
This is primarily intended for use by :mod:`mkname.mod.make_scifi`
when modifying names to make them seem more like names found in
pulp science fiction. The default values are listed in the example
`mkname` section above.


.. _vowels:

vowels
------
This defines the characters used as "vowels" by :mod:`mkname`. This
setting is primarily used to split names into syllables when generating
new names from multiple names from the database. The default value is
the list of English vowels, minus the letter `w`.

.. note:
    Yes, `w` is sometimes a vowel in English. It occurs in the Welsh
    loan words `cwm` and `crwth`. Why bring it up when it's only a
    few Welsh loan words and :mod:`mkname` doesn't define it as a
    vowel? Well, because it's the internet and someone would eventually
    complain if I didn't. Also, I just think it's a cool fact.


.. config_loc:

Configuration File Location
===========================
The following are the files where :mod:`mkname` looks for
configuration files.

*   In a dedicated `mkname.toml` or `mkname.cfg` file.
*   Within a `pyproject.toml` or `setup.cfg` file.

:mod:`mkname` will always look for these files in the current
working directory. If the command line tool or API call you
are using allows you to supply a configuration file path,
it will look for files of those names in that path if you
give it a path to a directory rather than a file.


.. config_load:

Loading Configuration
=====================
A configuration file doesn't need to have all keys for :mod:`mkname`
defined. To build the configuration, :mod:`mkname` will look for a
series of files, loading the configuration from each until it arrives
at the final configuration. Since the default configuration file
contains every key, this means that every key will eventually be
set regardless of whether you define it in a particular custom
config file or not.

Configuration is loaded in the following order:

*   The default configuration,
*   A `setup.cfg` file in the current working directory,
*   A `pyproject.toml` file in the current working directory (Python >= 3.11),
*   A `mkname.cfg` file in the current working directory,
*   A `mkname.toml` file in the current working directory (Python >= 3.11),
*   If a config file is explicitly passed to :mod:`mkname`, that file,
*   If a directory is explicitly passed to :mod:`mkname`, it will
    look for the following in that directory:
    *   `setup.cfg`,
    *   `pyproject.toml` (Python >= 3.11),
    *   `mkname.cfg`,
    *   `mkname.toml` (Python >= 3.11).

Since the values from the files are loaded on top of each other, files
loaded later will override values in files loaded earlier.


.. db_load:

Loading the Names Database
==========================
While :mod:`mkname` provides a :ref:`default_db`, it allows you to
create and supply your own names database. This means :mod:`mkname`
needs to have a way to decide which names database to use at runtime.


.. _db_search:

Database Search Order
---------------------
When selecting a names database to use at runtime, :mod:`mkname`
should search for a database in the following order:

1.  A file path given explicitly to :mod:`mkname`,
2.  A directory path that contains a file named `names.db` given
    explicitly to :mod:`mkname`,
3.  A path set in the :ref:`db_path` key in the configuration,
4.  A file named `names.db` in the current working directory,
5.  The default names database.

This means there are several different ways to use a customized
database when using :mod:`mkname` to generate names:

*   Place a custom names database in the current working directory.
*   Provide a configuration file that points to a custom names database.
*   Provide the path to the custom names database to :mod:`mkname`
    when generating the name. How you do this will vary depending on
    exactly what you are doing.
