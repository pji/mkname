.. _api:

##########
Public API
##########

The following are the functions that make up the public API of
:mod:`mkname`.


Name Generation and Selection
=============================
The following functions generate names:

.. autofunction:: mkname.build_compound_name
.. autofunction:: mkname.build_from_syllables
.. autofunction:: mkname.select_name


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
The following functions pull relevant information from the `names`
database used in generating or selecting names:

.. autofunction:: mkname.get_cultures
.. autofunction:: mkname.get_kinds
.. autofunction:: mkname.get_names
.. autofunction:: mkname.get_names_by_kind


Initialization
==============
The following functions are used to configure :mod:`mkname`:

.. autofunction:: mkname.get_config
.. autofunction:: mkname.get_db
