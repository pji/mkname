"""
test_init
~~~~~~~~~

Unit tests for :mod:`mkname.init`.
"""
import configparser
from pathlib import Path

import pytest

from mkname import init
import mkname.constants as c


# Fixtures.
@pytest.fixture
def default_config():
    """Pulls the default configuration values from the config file."""
    config = configparser.ConfigParser()
    config.read(c.DEFAULT_CONFIG)
    keys = ['mkname', 'mkname_files']
    return {k: dict(config[k]) for k in config if k in keys}


@pytest.fixture
def local_config():
    """Moves a config file into the current working directory,
    yields the contents of that config, then cleans up.
    """
    # Create the test config in the CWD.
    path = Path('tests/data/test_load_config.conf')
    link = Path('mkname.cfg')
    link.hardlink_to(path)

    # Send the contents of the config to the test.
    config = configparser.ConfigParser()
    config.read(link)
    keys = ['mkname', 'mkname_files']
    yield {k: dict(config[k]) for k in config if k in keys}

    # Clean up after test.
    if link.exists():
        link.unlink()


# Test get_config.
def test_get_config(default_config):
    """By default, load the configuration from the default configuration
    file stored in `mkname/mkname/data`.
    """
    assert init.get_config() == default_config


def test_get_config_with_local(local_config):
    """If there is a configuration file in the current working directory,
    :func:`mkname.init.get_config` should load the configuration from
    that file.
    """
    assert init.get_config() == local_config
