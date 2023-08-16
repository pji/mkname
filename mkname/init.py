"""
init
~~~~

Basic initialization functions for :mod:`mkname`.
"""
from configparser import ConfigParser
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import mkname.data


# Types.
Section = dict[str, str]
Config = dict[str, Section]


def get_config() -> Config:
    """Get the configuration."""
    # Start the config with the default values.
    default_path = get_default_path() / 'defaults.cfg'
    config = read_config_file(default_path)

    # If there is a local config file, override the default config
    # with the config from the local file.
    exts = ['cfg', 'conf', 'ini',]
    cwd = Path.cwd()
    for ext in exts:
        for local_path in cwd.glob(f'*.{ext}'):
            new = read_config_file(local_path)
            config.update(new)

    # Return the loaded configuration.
    return config


def get_default_path() -> Path:
    """Get the path to the default data files."""
    data_pkg = files(mkname.data)
    return Path(f'{data_pkg}')


def read_config_file(path: Path) -> Config:
    """Read an "INI" formatted configuration file.

    :param path: The path to the configuration file.
    :return: The contents of the configuration file as a :class:`dict`.
    :rtype: dict
    """
    config = ConfigParser()
    config.read(path)
    sections = ['mkname', 'mkname_files']
    return {k: dict(config[k]) for k in config if k in sections}
