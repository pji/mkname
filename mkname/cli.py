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


# Command parsing.
def parse_cli() -> None:
    """Response to commands passed through the CLI."""
    p = ArgumentParser(description='Randomized name construction.')
    p.add_argument(
        '--list_all_names', '-L',
        action='store_true',
        help='List all the names in the database.'
    )
    
    args = p.parse_args()
    
    config = mn.get_config()
    db_loc = mn.init_db(config['db_path'])
    
    if args.list_all_names:
        list_all_names(db_loc)
