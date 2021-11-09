###################
mkname Requirements
###################

The purpose of this document is to detail the requirements for the
`mkname` package. This is an initial take to help with planning. There
may be additional requirements or non-required features added in the
future.


Purpose
-------
The purposes of `mkname` are:

*   Be able to generate a randomized name for a person that seems
    vaguely plausible within the developer's cultural context
    (Midwestern United States)
*   Allow the ability to add new base names to use as building blocks
    for the created names without having to hard code them.


Functional Requirements
-----------------------
The following are the functional requirements for `mkname`:

1.  `mkname` can generate a given name.
2.  `mkname` can generate a family name.
3.  `mkname` can use a database of seed names as parts to create a
    randomized name.
4.  `mkname` can update the name seed database with new names.
5.  `mkname` can be used from the command line.
6.  `mkname` can be imported and used within other Python applications.
7.  `mkname` can have different sets of seed names to change the
    character of the generated names.

The following are not strictly requirements, but are features that
would be good to add in the future to allow the package to be useful
outside of the developer's limited cultural context.

1.  `mkname` can generate names that vaguely adhere cultural contexts
    beyond the developer's.
2.  `mkname` can use a database of undesirable names to avoid the
    creation of names that would lead to undesired reactions or
    results. (Preventing this algorithmically seems unlikely to be
    possible.)


Technical Requirements
----------------------
The following are the technical requirements for `mkname`:

1.  `mkname` will be written in Python.
2.  `mkname` will not hardcode seed names for use in name generation,
    but can come with an initial set of names to initialize the
    database.


Design Discussion
-----------------
This section discusses elements of the design of the `mkname` package.
It's intended as a way to think through design problems while they are
being solved. Therefore they may not accurately represent the current
state of the package.


Initialization
~~~~~~~~~~~~~~
In order to allow users to add names of their choosing to the database,
the database needs to be within the user's control. That's awkward if
the database is living within the package, so the option must exist for
the database to be in a different location. The root of their project
seems like a reasonable default location.

This raises a few problems that will need to be solved:

*   How does `mkname` know where to look for the database?
*   How does the database get created in that location?
*   How does `mkname` avoid spewing databases into new locations when
    code is run outside of the root of the project?


Database Location
~~~~~~~~~~~~~~~~~
`mkname` will need to go through a several step process to find the
database when it is run. Those steps are:

1.  Look for a file in a path passed to `mkname`.
2.  Look for a `db_path` key in a configuration file passed to `mkname`.
3.  Look for a `db_path` key in a configuration file in a default
    location.
4.  Look for the default database in the `mkname` package.

If a database doesn't exist at the discovered location:

*   If there is not a file or directory there, copy the default database
    to that location.
*   If there is a file or directory there, throw an exception.

If I only create databases when given a new path from the calling
application or a config file, then I think I avoid just spewing the
databases into every directory the code is called from.

The question of the DB's existence is handled through database
initialization. How will finding the database be handled? It should
probably be handled in the process of making the database connection.


Configuration Location
~~~~~~~~~~~~~~~~~~~~~~
`mkname` will need to go through a several step process to find the
configuration file that contains its configuration. Those steps are:

1.  Look for a file in a path passed to `mkname`.
2.  Look for a file in the current working directory.
3.  Look for the default config in the `mkname` package.

If a file is found, then the following steps are performed:

1.  The file is parsed with `ConfigParser`.
    a.  If successful: continue.
    b.  If failed: raise error.
2.  Search for a `mkname` section in the config.
    a.  If found: continue.
    b.  If not found: Add the default config to the config file.
3.  The `mkname` section is returned.

The location of the database makes 2b above a bit awkward. We can't
assume we know where the default database is located in the file system.
Therefore, the default configuration cannot be hardcoded into a config
file. It will have to be calculated at run time. That should be doable.

This will mean that neither a config file nor a database will be created
unless the user specifically wants them to be. Since it won't happen
automatically, I'll need to make sure the user has enough documentation
to realize they can have them created if they want.


Initialization Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Based on the discussion of database and config file locations, the
following are now requirements for `mkname`:

*   x `mkname` can be passed the location of a name database.
*   x `mkname` can be passed the location of a config file.
*   x `mkname` can look in the current working directory for a
    config file.
*   x `mkname` can create a new database in a given location.
*   x `mkname` can create a new configuration file in a given
    location.
*   x `mkname` can default to using the base database from the
    package.
*   x `mkname` can default to using default config.


Initialization Process
~~~~~~~~~~~~~~~~~~~~~~
Based on all of this, the initialization process probably looks like:

1.  `mkname` is invoked.
2.  Get the config.
    1.  If a config file is given and it doesn't exist: create it.
    2.  If a config file is given: read the config.
    3.  If not, use default config.
3.  Get the database location from the default config.
4.  Initialize the database:
    1.  If the database exists, continue.
    2.  If not, copy base data into a db at that location.
5.  Make the connection to the database.

This means users should go through the initialization process before
using any functions in mkname that make calls to the database. This
isn't really a surprise.


Command Line Usage
~~~~~~~~~~~~~~~~~~
The `mkname` package is intended to be called directly as well as
imported as a package. Direct use will be from the command line.
The goals for command line usage are:

*   x `mkname` can accept a config file as an argument.
*   x `mkname` allows users to choose which generation function to use.
*   x `mkname` can generate one name.
*   x `mkname` can generate multiple names.
*   `mkname` allows users to modify names.
*   x `mkname` allows users to display the names in the database.
*   `mkname` allows users to add names to the database.
*   `mkname` allows users to remove names from the database.
*   `mkname` allows users to backup the database.
*   `mkname` allows users to restore a database backup.
*   `mkname` does not allow users to alter the default database.
