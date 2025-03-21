"""
constants
~~~~~~~~~

Default configuration values for mknames.
"""
from mkname.init import get_config


# Read default config.
config = get_config()

# Word structure.
default = config['mkname']
CONSONANTS = default['consonants']
PUNCTUATION = default['punctuation']
SCIFI_LETTERS = default['scifi_letters']
VOWELS = default['vowels']

# Messages.
MSGS = {
    'en': {
        'add_success': 'Added {name} to {dst_path}.',
        'add_default_db': 'Cannot add to the default database.',
        'default_db_write': 'Cannot import to the default database.',
        'desc_mkname': (
            'Generate a random names or read data from a names database.'
        ),
        'desc_tools': 'Tools to work with mkname names databases.',
        'dup_success': 'The database has been copied to {dst_path}.',
        'dup_path_exists': 'Copy failed. Path {dst_path} exists.',
        'export_success': 'Database exported to {path}.',
        'id_collision': 'ID {id} already exists in database.',
        'import_success': 'Imported {src} to {dst}.',
        'invalid_format': 'Format {format} is unknown.',
        'new_success': 'The database has been created at {dst_path}.',
        'new_path_exists': 'Create DB failed. Path {dst_path} exists.',
        'option_conflict': 'Options {opts} cannot be used at the same time.',
        'read_path_not_exists': 'Read failed. Path {path} does not exist.',
        'unknown_field': 'Unknown list field {field}.',
        'write_path_exists': 'Write failed. Path {path} exists',
    },
}

# Define the values that will be imported with an asterisk.
__all__ = [
    # Common data.
    'CONSONANTS',
    'PUNCTUATION',
    'SCIFI_LETTERS',
    'VOWELS',

    # Administration.
    'MSGS',
]
