######
mkname
######

A Python package for building names by using other names as building
blocks.


What Does mkname Do?
====================
`mkname` uses a database of names to randomly generate names:

    >>> import mkname
    >>>
    >>> mkname.pick_name(kind='surname')
    ['Phan']
    >>> mkname.pick_name(kind='given', gender='male', num_names=4)
    ['Henry', 'Hector', 'Jimmie', 'Giovanni']
    >>> mkname.create_compound_name(culture='United States', gender='male')
    ['Damuel']
    >>> mkname.create_syllable_name(4)
    ['Betmahuret']


If you just want to generate a name and you don't want to write
any code around generating it, `mkname` can also be run from
the command line::

    $ mkname pick
    Cheryl
    $ mkname compound
    Awilson

You can access help on using `mkname` from the command line by
using the `-h` option::

    $ mkname -h
    
    usage: mkname [-h] mode ...
    
    Generate a random names or read data from a names database.
    
    positional arguments:
    ...


Features
========
The main features of `mkname` are:

*   Select a random name from the names database.
*   Modify generated names with `mod` functions.
*   Customize name generation by creating your own names database.
*   Add name generation to your Python code with the`mkname`
    package.
*   Generate names at the command line with the `mkname` tool.


Installation
============
`mkname` is available for install from PyPI with `pip`
or your favorite package manager::

    $ pip3 install mkname

The source code is available on GitHub if you'd rather install
it that way: `mkname <https://github.com/pji/mkname>`_.


What Changed in Version 0.2.4
=============================
The following changes were made in v0.2.4:

*   Moved dependency management to `poetry`.
*   Added ability to list the genders assigned to the names.
*   Added ability to duplicate the names database for customization.
*   Added tools for adding names to a names database.
*   Added `mkname_tools` script for administering the names database.
*   Explicitly pointing to a non-existent database will no longer
    create a new names database in that location.
*   Added new API functions that manage the database and configuration
    for you.
*   More documentation!


`mkname` and Cultural Bias
==========================
Names are influenced by the culture and experience of those doing
the naming. What sounds like a plausible name to me may not sound
like a plausible name to you. Even worse, what seems like an
acceptable name to my may be offensive to you. `mkname` is
sticking pieces of names together at random, it's very possible
the output could have undesirable connotations in its final
context.

The default names database supplied with
`mkname` is unavoidably biased by my culture, experience,
and the data I could find. To make `mkname` more useful
to more people, it also has the ability to use custom names
databases you create. The `mkname.tools` module and the
`mkname_tools` command line tool have features to help with this.

There are a few concepts like "letters," "consonants," and "vowels"
that are baked in right now but may not work for all languages
and cultures. If you find these are interfering with your use
of `mkname`, please feel free to open an issue on it. I can't
promise anything because I'm just one person doing this on my
free time, but I'll see what I can do.


'mkname' Test Package
=====================
Testing is automated with a combination of `make`, `pytest`,
and `tox`. To run a quick set of tests that just check against
your current version of Python::

    make test

To get the verbose output::

    make testv

To run the full suite of pre-commit tests::

    make pre
