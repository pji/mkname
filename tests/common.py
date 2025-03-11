"""
common
~~~~~~

Common functions for :mod:`mkname` tests.
"""
import csv

import mkname.model as m


def csv_matches_names(path, names):
    """Compare the names in the CSV file to the given names."""
    with open(path) as fh:
        reader = csv.reader(fh)
        results = [m.Name(*row) == name for row, name in zip(reader, names)]
    return results
