"""
__init__
~~~~~~~~

A Python module for creating names using other names as building blocks.
"""
from mkname import db
from mkname.mkname import (
    load_config,
    build_base_name,
    add_scifi_letters,
    garble
)


# Default values.
CONFIG_FILE = 'setup.cfg'
