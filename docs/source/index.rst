.. mkname documentation master file, created by
   sphinx-quickstart on Sat Aug 19 07:52:14 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mkname's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   self
   /api.rst
   /model.rst
   /customization.rst
   /tools.rst
   /requirements.rst


.. _intro:

Introduction to :mod:`mkname`
=============================
The :mod:`mkname` package is a Python package for building names by
using other names as building blocks.


Why?
====
It started with an update to a blackjack game I wrote as my first
project in Python. I wanted to have a bunch of computer players
playing with you, and I thought they should be randomly generated
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


How do I install it?
====================
The easiest way to install `mkname` is:

1.  Ensure you are using Python 3.10 or higher.
2.  Install from PyPI using pip: `pip install mkname`


How do I use `mkname` from the command line?
============================================
Once :mod:`mkname` is installed, you can run it from the command
line. You can get an overview of the available options by running
`mkname -h`. Below are examples of a few of those options.


How can I pick a random name from the database?
-----------------------------------------------
To pick a random name from the database use `mkname -p`::

    $ mkname
    Cheryl

To pick a name from the family names in the database, add `-l`::

    $ mkname -l
    Kaiser


How can I build a name from two names from the database?
--------------------------------------------------------
To pick a construct a name from two names from the database use
`mkname -c`::

    $ mkname -c
    Awilson

If you'd like the name to seem a bit more like something out of an
old pulp sci-fi novel, you can have it modified with `-m make_scifi`::

    $ mkname -cm make_scifi
    Xephanie

If `make_scifi` doesn't change it enough, you can try `-m garble`::

    $ mkname -cm garble
    Uaortiz


How can I build two names?
--------------------------
The `-n` option followed by a number will create that number of names::

    $ mkname -cm make_scifi -n 2
    Asteveq
    Qavel


Can I import :mod:`mkname` into my own Python code?
---------------------------------------------------
Yes, you can. For example, lets say you want to generate a compound
name using the names from the default database::

    >>> import mkname
    >>> names = mkname.get_names()
    >>> name = mkname.build_compound_name(names)

View the API documentation for more information.


What about cultural bias in :mod:`mkname`?
==========================================
Names are culturally specific things. What seems like a plausible name
to me may not sound like a plausible name to you. How names are tied to
gender may be different for you and me. Even worse, since this can
generate names from random pieces of other names, it's possible the
output can have undesirable connotations in its final context.

I am but one Midwestern U.S. farm boy working on this package for free.
I cannot promise it will work well for your needs. To allow for usage
in cultural contexts beyond my own, I have built it to be extensible.
You can replace the entire names database and the alphabet it uses if
you want. However there are concepts like "consonants", "vowels", and
"letters" that are baked in right now, which may not work for all
languages.

If there are changes I can make that will make it work better for you,
please let me know. I can't promise anything. Like I said above, I'm
not getting paid for this. But, I would like to make this useful for
more people.


How do I run the tests?
=======================
I'm using the `pytest` library for the unit tests. To just run those tests,
go to the root of your clone of the `mkname` repository and use the following
command::

    python3 -m pytest

The full suite of style checks, :mod:`mypy`, and such I use can be run
using a shortcut I have set up in the Makefile::

    make pre

.. note::
    `precommit.py` requires itself to be run from a virtual environment
    located in the `.venv` directory at the root of the repository. This
    is so I don't accidentally run it using my system's Python and then
    waste hours troubleshooting that mess again. If you want to disable
    this, you'll have to modify the script. The easiest way is probably
    commenting out the `check_venv()` call in `main()`.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
