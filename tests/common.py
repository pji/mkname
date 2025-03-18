"""
common
~~~~~~

Common functions for :mod:`mkname` tests.
"""
import csv
import sqlite3
from itertools import zip_longest
from operator import itemgetter

import mkname.model as m


__all__ = [
    'csv_matches_names',
    'db_matches_names',
    'file_matched_text',
]


def csv_matches_names(path, names):
    """Compare the names in the CSV file to the given names."""
    with open(path) as fh:
        reader = csv.reader(fh)
        rows = [m.Name(*row) for row in reader]
        for row, name in zip_longest(rows, names):
            try:
                assert row.astuple() == name.astuple()
            except AssertionError:
                raise ValueError(f'{row}, {name}')
        results = [
            row == name for row, name
            in zip_longest(rows, names)
        ]
    return all(results)


def db_matches_names(path, names):
    """Compare the names in the DB to the given names."""
    query = 'SELECT * FROM names'
    con = sqlite3.Connection(path)
    qresult = con.execute(query)
    ordered = sorted([row for row in qresult], key=itemgetter(0))
    rows = [m.Name(*row) for row in ordered]
    for row, name in zip_longest(rows, names):
        try:
            assert row.astuple() == name.astuple()
        except AssertionError:
            raise ValueError(f'{row}, {name}')
    results = [row == name for row, name in zip_longest(rows, names)]
    con.close()
    return all(results)


def file_matched_text(path, text):
    """Compare the text in the file to the given text."""
    return path.read_text() == text
