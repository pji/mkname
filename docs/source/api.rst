.. testsetup:: api

    from mkname import *
    from mkname.model import Name
    import yadr.operator as yop
    yop.random.seed('spam123')

.. testsetup:: config

    from mkname import get_config, get_db

.. testsetup:: mod

    from mkname.mod import *

.. _api:

##########
Public API
##########

The following are the functions that make up the public API of
:mod:`mkname`.

.. automodule:: mkname.mkname
.. automodule:: mkname.mod
.. automodule:: mkname.db
.. automodule:: mkname.init
