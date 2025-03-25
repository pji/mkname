.. mkname documentation master file, created by
   sphinx-quickstart on Sat Aug 19 07:52:14 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _intro:

######
mkname
######

:mod:`mkname` is a Python package for building names by
using other names as building blocks.


.. _toc:

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   self
   /api.rst
   /config.rst
   /model.rst
   /db.rst
   /customization.rst
   /tools.rst


.. _what:

What Does `mkname` Do?
======================
:mod:`mkname` uses a :ref:`database of names<names_db>` to randomly
generate names:

.. testsetup:: index
    
    from unittest.mock import patch
    test_db = 'tests/data/big_names.db'
    patch('mkname.init.get_default_db', return_value=test_db)
    import yadr.operator as yop
    yop.random.seed('spam123')

.. doctest:: index

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
any code around generating it, :mod:`mkname` can also be run from
the command line::

    $ mkname pick
    Cheryl
    $ mkname compound
    Awilson

You can access help on using `mkname` from the command line by
using the -h option::

    $ mkname -h
    
    usage: mkname [-h] mode ...
    
    Generate a random names or read data from a names database.
    
    positional arguments:
    ...


.. _features:

Features
========
The main features of :mod:`mkname` are:

*   Select a random name from the :ref:`names database<names_db>`.
*   Modify generated names with :ref:`mod<mod_api>` functions.
*   Customize name generation by creating your own
    :ref:`names database<names_db>`.
*   Add name generation to your Python code with the :mod:`mkname`
    package.
*   Generate names at the command line with the `mkname` tool.


.. installation:

Installation
============
:mod:`mkname` is available for install from PyPI with :mod:`pip`
or your favorite package manager::

    $ pip3 install mkname

The source code is available on GitHub if you'd rather install
it that way: `mkname <https://github.com/pji/mkname>`_.


.. bias:

`mkname` and Cultural Bias
==========================
Names are influenced by the culture and experience of those doing
the naming. What sounds like a plausible name to me may not sound
like a plausible name to you. Even worse, what seems like an
acceptable name to my may be offensive to you. :mod:`mkname` is
sticking pieces of names together at random, it's very possible
the output could have undesirable connotations in its final
context.

The :ref:`default names database<default_db>` supplied with
:mod:`mkname` is unavoidably biased by my culture, experience,
and the data I could find. To make :mod:`mkname` more useful
to more people, it also has the ability to use :ref:`custom names
databases<db_customization>` you create. The :mod:`mkname.tools`
module and the `mkname_tools` command line tool have features
to help with this.

There are a few concepts like "letters," "consonants," and "vowels"
that are baked in right now but may not work for all languages
and cultures. If you find these are interfering with your use
of :mod:`mkname`, please feel free to open an issue on it. I
can't promise anything because I'm just one person doing this on
my free time, but I'll see what I can do.


`mkname` Test Package
=====================
Testing is automated with a combination of `make`, :mod:`pytest`,
and :mod:`tox`. To run a quick set of tests that just check
against your current version of Python::

    make test

To get the verbose output::

    make testv

To run the full suite of pre-commit tests::

    make pre


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
