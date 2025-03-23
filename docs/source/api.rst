.. testsetup:: api

    from mkname import *
    from mkname.model import Name
    import yadr.operator as yop
    yop.random.seed('spam123')

.. _api:

##########
Public API
##########

The following are the functions that make up the public API of
:mod:`mkname`.


Name Generation and Selection
=============================
The following functions generate names:

.. autofunction:: mkname.create_compound_name
.. autofunction:: mkname.create_syllable_name
.. autofunction:: mkname.pick_name


Manually Configured Generation and Selection
--------------------------------------------
The following functions can also generate names, but they require
a little more work on your part to manage the configuration. Only
use these if, for some reason, you need to get between the process
of loading the configuration or names from the names database and
the generation of the name:

.. autofunction:: mkname.build_compound_name
.. autofunction:: mkname.build_from_syllables
.. autofunction:: mkname.select_name


Name Listing
============
The following function will list the names in the current
names database.

.. autofunction:: mkname.list_names


Name Modification
=================
The following functions modify names:

.. autofunction:: mkname.add_letters
.. autofunction:: mkname.add_punctuation
.. autofunction:: mkname.compound_names
.. autofunction:: mkname.double_letter
.. autofunction:: mkname.double_vowel
.. autofunction:: mkname.garble
.. autofunction:: mkname.make_scifi
.. autofunction:: mkname.translate_characters
.. autofunction:: mkname.vulcanize


Data Enumeration
================
Information on the data enumeration functions can be found in
:ref:`db_read`.


Initialization
==============
Information on the data enumeration functions can be found in
:ref:`config_api`.
