"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
from mkname.init import get_config, get_default_path


# Path roots.
DATA_ROOT = get_default_path()
DEFAULT_CONFIG = DATA_ROOT / 'defaults.cfg'

# Read default config.
config = get_config()

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
