"""
mkname
~~~~~~

Tools for building names.
"""
import configparser
from typing import Mapping


# Default values.
CONFIG_FILE = 'setup.cfg'


# Initialization functions.
def load_config(filepath: str) -> Mapping:
    """Load the configuration."""
    config = configparser.ConfigParser()
    config.read(filepath)
    return config['mkname']
