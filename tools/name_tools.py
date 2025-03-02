"""
name_tools
~~~~~~~~~~

Tools for changing the names database.
"""
from collections.abc import Sequence
import csv


# Data preparation functions.
def read_csv(
    path: str,
    head_rows: int = 0,
    col: int | None = None
) -> list[list[str]]:
    """Extract data from CSV files."""
    with open(path) as fh:
        reader = csv.reader(fh)
        lines = [line for line in reader]
    if head_rows:
        lines = lines[head_rows:]
    if col is not None:
        lines = [[line[col],] for line in lines]
    return lines


def write_csv(names: list[list[str]], path: str) -> None:
    """Save data to a CSV file."""
    with open(path, 'w') as fh:
        writer = csv.writer(fh)
        for line in names:
            writer.writerow(line)


def decap(name: str, mcc_intercap: bool = True) -> str:
    """Decapitalize a name in all capital letters."""
    name = name.title()
    if mcc_intercap and name.startswith('Mcc'):
        name = f'McC{name[3:]}'
    return name


def process_census_surname_list(path: str, url: str, year: int) -> None:
    """Turn the U.S. Census surname list into serialized Name objects."""
    lines = read_csv(path, 3, 0)
    y = str(year)
    names = [
        ['', decap(line[0]), url, 'United States', y, 'none', 'surname']
        for line in lines
    ]
    write_csv(names, f'done_{path}')


def reindex_names_csv() -> None:
    """Add sequential ID to each record in the names CSV file."""
    path = 'src/mkname/data/names.csv'
    names = read_csv(path)
    names = [[n, *record[1:]] for n, record in enumerate(names)]
    write_csv(names, path)


if __name__ == '__main__':
    reindex_names_csv()
