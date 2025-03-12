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

# Messages.
MSGS = {
    'en': {
        'dup_success': 'The database has been copied to {dst_path}.',
        'dup_path_exists': 'Copy failed. Path {dst_path} exists.',
        'export_success': 'Database exported to {path}.',
        'id_collision': 'ID {id} already exists in database.',
        'import_success': 'Imported {src} to {dst}.',
        'invalid_format': 'Format {format} is unknown.',
        'read_path_not_exists': 'Read failed. Path {path} does not exist.',
        'write_path_exists': 'Write failed. Path {path} exists',
    },
}

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

    # Administration.
    'MSGS',
]
