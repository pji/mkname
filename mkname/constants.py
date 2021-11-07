"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
from pathlib import Path


# Path roots.
PKG_ROOT = Path(__file__).parent
DATA_ROOT = PKG_ROOT / 'data'

# File locations.
CONFIG_FILE = DATA_ROOT / 'defaults.cfg'
DEFAULT_CONFIG = DATA_ROOT / 'defaults.cfg'
DEFAULT_DB = DATA_ROOT / 'names.db'
LOCAL_CONFIG = 'mkname.cfg'
LOCAL_DB = 'names.db'

# Word structure.
PUNCTUATION = "'- "
CONSONANTS = 'bcdfghjklmnpqrstvwxz'
VOWELS = 'aeiouy'
SCIFI_LETTERS = 'kqxz'
