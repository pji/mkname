.. _model:

#########
Name Data
#########
A "name" in :mod:`mkname` is stored as a :class:`mkname.model.Name`
object with the following fields:

*   id
*   name
*   source
*   culture
*   date
*   gender
*   kind

For example, let's say you want to add the name "Graham," as in
the first name of "Graham Chapman" from Monty Python::

    >>> from mkname.model import Name
    >>>
    >>> name = Name(
    ...     id=0,
    ...     name='Graham',
    ...     source='https://montypython.com',
    ...     culture='MontyPython',
    ...     date=1941,
    ...     gender='python',
    ...     kind='given'
    ... )
    >>> name.name
    'Graham'


.. _name_fields:

Name Data Fields
================
The following are the data fields stored for a name in the names
database.


id
--
This is a simple serial number used to uniquely identify the
:class:`mkname.model.Name` object when it is serialized in a
database or other output file.


name
----
This is the name itself as a :class:`str` object.

The only limitation on this, beyond any set by the :class:`str` class,
is that it has a maximum size limit of 64 characters. This limit only
exists to provide a boundary for the database. Future versions of
:mod:`mkname` could increase it if there are cultures with names
longer than 64 characters.


source
------
This is the source where the name was found as a :class:`str` object.

It's intended to be the specific URL for data the name was pulled from.
For example, some of the names in the default database were pulled from
the U.S. Census's list of most common surnames in 2010. The source field
for those names is the URL for that report on the U.S. Census website::

    https://www.census.gov/topics/population/genealogy/data/2010_surnames.html

There are three main reasons the source data is kept with the name:

*   It provides context for why the name is in the database.
*   It credits the people or organization that gathered the name data.
*   It allows data to be identified and pulled from the database if
    needed for some reason in the future.

The maximum length of a source is 128 characters.


culture
-------
This is the culture the name is from as a :class:`str` object.

As used in the default database, this is the nation associated with
the source I got the name from. However, this is intended to be
broader than that. It's, essentially, any grouping of people you
wish to associate the name to. For example, if you were adding
the names from the works of J. R. R. Tolkien, you may
mark the names of hobbits as "Hobbit" and those of dwarves as
"Dwarf." And, of course, you can split the elven names into "Sindar"
and "Quenyan," and so on.

The purpose of this field is to allow name generation to be narrowed
by culture. If you want to generate the name of someone from the
Roman Empire, you can limit name generation to just the "Roman"
culture.

The maximum length of a culture is 64 characters.


date
----
The date associated with the data the name was taken from as an
:class:`int` object.

As used in the default database, this is the year for the name in
the Common Era (C.E.). Negative values are Before Common Era (B.C.E.).

The date is stored in the SQLite database as an `INTEGER`. This can be
up to an 8 byte, signed number, in case you are projecting names that
far into the future or the past.


gender
------
This is the "gender" of the name as a :class:`str` object.

Name data, especially "given" name data, tends to associate a
gender to a name. This gender is tracked in the gender field
for the record, so it can be used to filter the names used
when generating a name.

.. note:
    :mod:`mkname` wasn't built with the idea of surnames needing
    to match the gender of the given name, which creates a
    difficulty for names in cultures where that is needed, such
    as Russian. At time of writing, the "male" and "female"
    versions of Russian surnames are stored as separate names,
    so you'll need to filter the surnames by gender during
    generation to insure agreement between the gender of the
    given and surnames. Future versions may correct this, if
    it would be useful.

The maximum length of a gender is 64 characters.


kind
----
This is the position or function of the name as a :class:`str`
object.

As used in the default database, there are two kinds of names:

*   *given:* The name associated with the individual. In the United
    States this tends to be the name listed first, i.e. the "first
    name," but that's not true of all cultures.
*   *surname:* The name associated with a family. In the United
    States this tends to be the name listed last, i.e. the "last
    name," but that is not true for all cultures.

The maximum length of a kind is 16 characters.


.. _names_db:

The Names Database
==================
The *names database* is a SQLite database used by :mod:`mkname` to
store the data used to generate names. It consists of a single table:

.. list-table::
   :widths: 100
   :header-rows: 1

   * - names
   * - (PK) id
   * - name
   * - source
   * - culture
   * - data
   * - gender
   * - kind

A description of each field can be found in the "Name Data Fields"
section above.


.. _default_db:

The Default Database
--------------------
The *default database* is a names database that comes with the
:mod:`mkname` package. It's intended to provide a basic set of
names data for the generation of names.

The default database is definitely biased towards the culture of
the midwestern United States in 2025, but I'd be happy to expand
its usefulness. The main limitation right now is my inability to
read languages other than English well enough to be able to track
down and understand census data in other languages. Though,
admittedly, I haven't looked at census data for Canada, the United
Kingdom, Australia, or New Zealand yet, either.

The data from `Name Census <https://census.name>`_ looks promising,
but it also looks like it requires licensing to use. This is
understandable. Collecting name data from around the world isn't
easy. However, it means I can't include data from Name Census in
the default database. :mod:`mkname.tools` does have the ability
to import data from Name Census to a new names database, though,
so if you would rather use their data than the default database,
you should be able to acquire the needed licenses and do so.


.. _names_serialization:

Names Serialization
===================
:mod:`mkname` supports exporting the contents of a names database
to a comma separated values (CSV) file and importing that CSV
files back into a names database. This is largely intended to
make it easier to customize the contents of a names database for
your needs.

The exported CSV file will have the same structure as the names
table of a names database as described in "The Names Database"
above. The tools for importing and exporting a names database
as a CSV file are found in :mod:`mkname.tools` or in the
`mkname_tools` command line script.
