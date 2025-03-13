"""
cli
~~~

Command line interface for the mkname package.
"""
from argparse import ArgumentParser, Namespace, _SubParsersAction
from collections.abc import Callable, Sequence
from pathlib import Path

from mkname import db
from mkname import mkname as mn
from mkname.constants import MSGS
from mkname.init import get_config, get_db
from mkname.mod import mods
from mkname.model import Name, Section
from mkname.tools import *


# Typing.
Subparser = Callable[[_SubParsersAction], None]
Registry = dict[str, dict[str, Subparser]]


# Command registration.
subparsers: Registry = {'mkname_tools': {}}


def subparser(script: str) -> Callable[
    [Callable[[_SubParsersAction], None]],
    Callable[[_SubParsersAction], None]
]:
    def decorator(
        fn: Callable[[_SubParsersAction], None]
    ) -> Callable[[_SubParsersAction], None]:
        """A decorator for registering subparsers.

        :param fn: The function being registered.
        :return: The registered :class:`collections.abc.Callable`.
        :rtype: collections.abc.Callable
        """
        key = fn.__name__.split('_', 1)[-1]
        subparsers[script][key] = fn
        return fn
    return decorator


# mkname commands.
def build_compound_name(names: Sequence[Name], config: Section) -> str:
    """Command script for constructing a name from two names in
    the database.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param config: The configuration data for :mod:`mkname`.
    :returns: A :class:`str` object.
    :rtype: str
    """
    name = mn.build_compound_name(
        names,
        config['consonants'],
        config['vowels']
    )
    return name


def build_syllable_name(
    names: Sequence[Name],
    config: Section,
    num_syllables: int
) -> str:
    """Command script for constructing a name from the syllables of
    names in the database.

    :param names: A list of Name objects to use for constructing
        the new name.
    :param config: The configuration data for :mod:`mkname`.
    :param num_syllables: The number of syllables in the constructed
        name.
    :returns: A :class:`str` object.
    :rtype: str
    """
    name = mn.build_from_syllables(
        num_syllables,
        names,
        config['consonants'],
        config['vowels']
    )
    return name


def duplicate_db(dst: str) -> str:
    """Duplicate the names DB to the given path."""
    dst_path = Path(dst)
    if dst_path.exists():
        return MSGS['en']['dup_path_exists'].format(dst_path=dst_path)
    db.duplicate_db(dst_path)
    return MSGS['en']['dup_success'].format(dst_path=dst_path)


def list_all_names(names: Sequence[Name]) -> tuple[str, ...]:
    """Command script to list all the names in the database.

    :param names: A list of Name objects in the database.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    return tuple(name.name for name in names)


def list_cultures(db_loc: Path) -> tuple[str, ...]:
    """A command script to list the unique cultures in the database.

    :param db_loc: The path to the mkname database.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    return db.get_cultures(db_loc)


def list_genders(db_loc: Path) -> tuple[str, ...]:
    """A command script to list the unique genders in the database.

    :param db_loc: The path to the mkname database.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    return db.get_genders(db_loc)


def modify_name(name: str, mod_name: str) -> str:
    """A command script to use the given simple mod on the name.

    :param name: The name to modify.
    :param mod: The mod to use on the name.
    :returns: A :class:`str` object.
    :rtype: str
    """
    mod = mods[mod_name]
    return mod(name)


def pick_name(names: Sequence[Name]) -> str:
    """The command script to select a name from the database.

    :param names: A list of Name objects to use for constructing
        the new name.
    :returns: A :class:`str` object.
    :rtype: str
    """
    name = mn.select_name(names)
    return name


# mkname_tools command modes.
def mode_export(args: Namespace) -> None:
    """Execute the `export` command for `mkname_tools`."""
    export(dst_path=args.output)
    print(MSGS['en']['export_success'].format(path=args.output))
    print()


def mode_import(args: Namespace) -> None:
    """Execute the `import` command for `mkname_tools`."""
    try:
        import_(
            dst_path=args.output,
            src_path=args.input,
            format=args.format,
            source=args.source,
            date=args.date,
            kind=args.kind
        )
        print(MSGS['en']['import_success'].format(
            src=args.input,
            dst=args.output,
        ))
    except DefaultDatabaseWriteError:
        print(MSGS['en']['default_db_write'])
    print()


# Output.
def write_output(lines: Sequence[str] | str) -> None:
    """Write the output to the terminal.

    :param lines: The output to write to the terminal.
    :returns: `None`.
    :rtype: NoneType
    """
    if isinstance(lines, str):
        lines = [lines, ]

    for line in lines:
        print(line)


# Command parsing.
def parse_cli() -> None:
    """Response to commands passed through the CLI.

    :returns: `None`.
    :rtype: NoneType
    """
    # Set up the command line interface.
    p = ArgumentParser(
        description='Randomized name construction.',
        prog='mkname',
    )
    p.add_argument(
        '--compound_name', '-c',
        help='Construct a name from two names in the database.',
        action='store_true'
    )
    p.add_argument(
        '--config', '-C',
        help='Use the given custom config file.',
        action='store',
        type=str
    )
    p.add_argument(
        '--duplicate_db', '-D',
        help='Duplicate the names DB for customization.',
        action='store',
        type=str
    )
    p.add_argument(
        '--first_name', '-f',
        help='Generate a given name.',
        action='store_true'
    )
    p.add_argument(
        '--gender', '-g',
        help='Generate a name from the given gender.',
        action='store',
        type=str
    )
    p.add_argument(
        '--list_genders', '-G',
        help='List all the genders in the database.',
        action='store_true'
    )
    p.add_argument(
        '--last_name', '-l',
        help='Generate a surname.',
        action='store_true'
    )
    p.add_argument(
        '--culture', '-k',
        help='Generate a name from the given culture.',
        action='store',
        type=str
    )
    p.add_argument(
        '--list_cultures', '-K',
        help='List all the cultures in the database.',
        action='store_true'
    )
    p.add_argument(
        '--list_all_names', '-L',
        help='List all the names in the database.',
        action='store_true'
    )
    p.add_argument(
        '--modify_name', '-m',
        help='Modify the name.',
        action='store',
        choices=mods
    )
    p.add_argument(
        '--num_names', '-n',
        help='The number of names to create.',
        action='store',
        type=int,
        default=1
    )
    p.add_argument(
        '--pick_name', '-p',
        help='Pick a random name from the database.',
        action='store_true'
    )
    p.add_argument(
        '--syllable_name', '-s',
        help='Construct a name from the syllables of names in the database.',
        action='store',
        type=int
    )
    args = p.parse_args()

    # Set up the configuration.
    config_file = ''
    if args.config:
        config_file = args.config
    config = get_config(config_file)['mkname']
    db_loc = get_db(config['db_path'])

    # Get names for generation.
    if args.first_name:
        names = db.get_names_by_kind(db_loc, 'given')
    elif args.last_name:
        names = db.get_names_by_kind(db_loc, 'surname')
    else:
        names = db.get_names(db_loc)
    if args.culture:
        names = [name for name in names if name.culture == args.culture]
    if args.gender:
        names = [name for name in names if name.gender == args.gender]

    # Generate the names, storing the output.
    lines = []
    for _ in range(args.num_names):
        if args.compound_name:
            name = build_compound_name(names, config)
            lines.append(name)
        if args.list_all_names:
            names = list_all_names(names)
            lines.extend(names)
        if args.list_cultures:
            cultures = list_cultures(db_loc)
            lines.extend(cultures)
        if args.list_genders:
            genders = list_genders(db_loc)
            lines.extend(genders)
        if args.pick_name:
            name = pick_name(names)
            lines.append(name)
        if args.syllable_name:
            name = build_syllable_name(names, config, args.syllable_name)
            lines.append(name)

    if args.modify_name:
        lines = [modify_name(line, args.modify_name) for line in lines]

    # Administer the database.
    if args.duplicate_db:
        msg = duplicate_db(args.duplicate_db)
        lines.append(msg)

    # Write out the output.
    write_output(lines)


def parse_mkname_tools() -> None:
    """Response to commands passed through the CLI.

    :returns: `None`.
    :rtype: NoneType
    """
    # Get the valid subparsers.
    subparsers_list = ', '.join(key for key in subparsers['mkname_tools'])

    # Set up the command line interface.
    p = ArgumentParser(
        description='Randomized name construction.',
        prog='mkname',
    )
    spa = p.add_subparsers(
        help=f'Available modes: {subparsers_list}',
        metavar='mode',
        required=True
    )
    for subparser in subparsers['mkname_tools']:
        subparsers['mkname_tools'][subparser](spa)
    args = p.parse_args()
    args.func(args)


# mkname_tools command subparsing.
@subparser('mkname_tools')
def parse_export(spa: _SubParsersAction) -> None:
    """Parse the `export` command for `mkname_tools`."""
    sp = spa.add_parser(
        'export',
        description='Export name data to a CSV file.'
    )
    sp.add_argument(
        '-o', '--output',
        help='The path to export the data to.',
        action='store',
        default='names.csv',
        type=str
    )
    sp.set_defaults(func=mode_export)


@subparser('mkname_tools')
def parse_import(spa: _SubParsersAction) -> None:
    """Parse the `import` command for `mkname_tools`."""
    formats = ', '.join(format for format in INPUT_FORMATS)
    sp = spa.add_parser(
        'import',
        description='Import name data from a file.'
    )
    sp.add_argument(
        '-d', '--date',
        help='The date for the names.',
        action='store',
        default=1970,
        type=int
    )
    sp.add_argument(
        '-f', '--format',
        help=(
            'The format of the input file. '
            f'The supported formats are: {formats}'
        ),
        action='store',
        default='csv',
        type=str
    )
    sp.add_argument(
        '-g', '--gender',
        help='The gender for the names.',
        action='store',
        default='unknown',
        type=str
    )
    sp.add_argument(
        '-i', '--input',
        help='The path to import the data from.',
        action='store',
        default='names.csv',
        type=str
    )
    sp.add_argument(
        '-k', '--kind',
        help='The kind for the names.',
        action='store',
        default='unknown',
        type=str
    )
    sp.add_argument(
        '-o', '--output',
        help='The path to import the data to.',
        action='store',
        default='names.db',
        type=str
    )
    sp.add_argument(
        '-s', '--source',
        help='The source of the input file.',
        action='store',
        default='unknown',
        type=str
    )
    sp.set_defaults(func=mode_import)
