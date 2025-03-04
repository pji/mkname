"""
name_tools
~~~~~~~~~~

Tools for changing the names database.
"""
from collections.abc import Sequence
import csv


# Data preparation functions.
def process_census_surname_list(path: str, url: str, year: int) -> None:
    """Turn the U.S. Census surname list into serialized Name objects."""
    lines = read_csv(path, 3, 0)
    y = str(year)
    names = [
        ['', decap(line[0]), url, 'United States', y, 'none', 'surname']
        for line in lines
    ]
    write_csv(names, f'done_{path}')
