"""
common
~~~~~~

Common functions for :mod:`mkname` tests.
"""
import csv
import sqlite3
from itertools import zip_longest

import mkname.model as m


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
    rows = [m.Name(*row) for row in qresult]
    for row, name in zip_longest(rows, names):
        try:
            assert row.astuple() == name.astuple()
        except AssertionError:
            raise ValueError(f'{row}, {name}')
    results = [row == name for row, name in zip_longest(rows, names)]
    con.close()
    return all(results)
