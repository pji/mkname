"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
import configparser
from importlib.resources import files
from pathlib import Path

import mkname.data


# Path roots.
data_pkg = files(mkname.data)
data_pkg_str = str(data_pkg)
DATA_ROOT = Path(data_pkg_str)
DEFAULT_CONFIG = DATA_ROOT / 'defaults.cfg'

# Read deafult config.
config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG)

# File locations.
locs = config['mkname_files']
CONFIG_FILE = DATA_ROOT / locs['config_file']
DEFAULT_DB = DATA_ROOT / locs['default_db']
LOCAL_CONFIG = DATA_ROOT / locs['local_config']
LOCAL_DB = DATA_ROOT / locs['local_db']

# Word structure.
default = config['mkname']
CONSONANTS = default['consonants']
PUNCTUATION = default['punctuation']
SCIFI_LETTERS = default['scifi_letters']
VOWELS = default['vowels']

# Define the values that will be imported with an asterisk.
__all__ = [
    # Common paths.
    'CONFIG_FILE',
    'DATA_ROOT',
    'DEFAULT_CONFIG',
    'DEFAULT_DB',
    'LOCAL_CONFIG',
    'LOCAL_DB',

    # Common data.
    'CONSONANTS',
    'PUNCTUATION',
    'SCIFI_LETTERS',
    'VOWELS',
]
