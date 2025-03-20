.. _model:

#########
Name Data
#########

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
