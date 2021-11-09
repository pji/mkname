"""
cli
~~~

Command line interface for the mkname package.
"""
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from mkname import db
from mkname import mkname as mn


# Commands.
def list_all_names(db_loc: Union[str, Path]) -> None:
    """List all the names in the database."""
    names = db.get_names(db_loc)
    lines = [name.name for name in names]
    for line in lines:
        print(line)


def pick_name(db_loc: Union[str, Path]) -> None:
    """Select a name from the database."""
    names = db.get_names(db_loc)
    name = mn.select_name(names)
    print(name)


# Command parsing.
def parse_cli() -> None:
    """Response to commands passed through the CLI."""
    p = ArgumentParser(description='Randomized name construction.')
    p.add_argument(
        '--config', '-c',
        help='Use the given custom config file.',
        action='store',
        type=str
    )
    p.add_argument(
        '--list_all_names', '-L',
        help='List all the names in the database.',
        action='store_true'
    )
    p.add_argument(
        '--pick_name', '-p',
        help='Pick a random name from the database.',
        action='store_true'
    )
    
    args = p.parse_args()
    
    config_file = ''
    if args.config:
        config_file = args.config
    
    config = mn.get_config(config_file)
    db_loc = mn.init_db(config['db_path'])
    
    if args.list_all_names:
        list_all_names(db_loc)
    if args.pick_name:
        pick_name(db_loc)
