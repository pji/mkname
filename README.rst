######
mkname
######

A Python package for building names by using other names as building
blocks.


Why?
====
It started with an update to a blackjack game I wrote as my first
project in Python. I wanted to have a bunch of computer players
playing with you, and thought they should be randomly generated
with randomly generated names. Then it came up in a few other things
I wrote, so I figured I'd turn it into a package.


What does it do?
================
It pulls random names from a database, and can modify those names
before returning them. Major features include:

*   Use parts of multiple names to construct a new name.
*   Modify the selected or constructed names.
*   Use a default database of names.
*   Use your own database of names.
*   Import into your Python code as a package.
*   Use from the command line.


How do I run it?
================
The easiest way to install and run `mkname` is:

1.  Ensure you are using Python 3.10 or higher.
2.  Install from PyPI using pip: `pip install mkname`
3.  Run the following command to see the options: `mkname -h`

It should also be able to be imported into your Python code as a package.


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
*   More documentation!


How do I run the tests?
=======================
Testing is automated with a combination of `make`, :mod:`pytest`,
and :mod:`tox`. To run a quick set of tests that just check
against your current version of Python::

    make test

To get the verbose output::

    make testv

To run the full suite of pre-commit tests::

    make pre
