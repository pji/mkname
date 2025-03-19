.. _configuration:

##################
Configuring mkname
##################

Configuring :mod:`mkname` can be done with file formated in the INI-like
style supported by :mod:`configparser`. The following document will go
over:

*   The supported keys and what they do.
*   How the configuration is loaded at run time.


.. _config_keys:

Configuration Keys
==================
Within the configuration file, :mod:`mkname` looks for a section named
`mkname`::

    [mkname]
    consonants = bcdfghjklmnpqrstvwxz
    db_path = 
    punctuation = '-.?!/:@+|•
    scifi_letters = kqxz
    vowels = aeiouy

This means :mod:`mkname` can either be in its own configuration file
or in a file that contains the configuration for multiple packages,
such as `setup.cfg`.

The keys that can be set in the `mkname` section are:

*   consonants
*   db_path
*   punctuations
*   scifi_letters
*   vowels


consonants
----------
This defines the characters used as "consonants" by :mod:`mkname`. This
setting is primarily used to split names into syllables when generating
new names from multiple names from the database. The default value is
the standard list of English consonants, minus the letter `y`.


db_path
-------
This sets the names database used by :mod:`mkname`. It can be used to
have :mod:`mkname` use a custom names database rather than the default
names database. The default value is an empty string, which causes
:mod:`mkname` to go to the next step in the database search order.


punctuations
------------
This defines the characters used as punctuation marks by :mod:`mkname`.
This is primarily intended for use by :func:`mkname.mod.add_punctuation`
when modifying names to add punctuation marks. The default values are
listed in the example `mkname` section above.


scifi_letters
-------------
The defines the characters used as "scifi letters" by :mod:`mkname`.
This is primarily intended for use by :mod:`mkname.mod.make_scifi`
when modifying names to make them seem more like names found in
pulp science fiction. The default values are listed in the example
`mkname` section above.


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
