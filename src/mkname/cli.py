"""
cli
~~~

The :mod:`mkname` package has two command line utilities:
*   `mkname`
*   `mkname_tools`

`mkname`
========
The `mkname` utility allows you to generate random names at the command
line::

    $ mkname
    Barron

The available options and what they do can be found in the help::

    $ mkname -h


`mkname_tools`
=============
The `mkname_tools` utility allows you to perform administrative actions
for `mkname`. For more information, view the help::

    $ mkname_tools -h

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
def mode_add(args: Namespace) -> None:
    """Execute the `add` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = []

    try:
        add(
            dst_path=args.db,
            name=args.name,
            source=args.source,
            culture=args.culture,
            date=args.date,
            gender=args.gender,
            kind=args.kind
        )
        msg = MSGS['en']['add_success'].format(
            name=args.name,
            dst_path=args.db
        )
    except DefaultDatabaseWriteError:
        msg = MSGS['en']['add_default_db']

    lines.append(msg)
    write_output(lines)


def mode_copy(args: Namespace) -> None:
    """Execute the `copy` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = []

    # Determine the path for the copy.
    path = Path('names.db')
    if args.output:
        path = Path(args.output)
    if path.is_dir():
        path = path / 'names.db'

    # Do not overwrite existing files.
    if path.exists():
        msg = MSGS['en']['dup_path_exists'].format(dst_path=path)
        lines.append(msg)

    # Copy the database to the path.
    else:
        db.duplicate_db(path)
        msg = MSGS['en']['dup_success'].format(dst_path=path.resolve())
        lines.append(msg)

    # Write any messages to standard out.
    write_output(lines)


def mode_export(args: Namespace) -> None:
    """Execute the `export` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    db_path = get_db_from_invoation(args)
    export(dst_path=args.output, src_path=db_path)
    print(MSGS['en']['export_success'].format(path=args.output))
    print()


def mode_import(args: Namespace) -> None:
    """Execute the `import` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    try:
        import_(
            dst_path=args.output,
            src_path=args.input,
            format=args.format,
            source=args.source,
            date=args.date,
            kind=args.kind,
            update=args.update
        )
        print(MSGS['en']['import_success'].format(
            src=args.input,
            dst=args.output,
        ))
    except DefaultDatabaseWriteError:
        print(MSGS['en']['default_db_write'])
    print()


def mode_list(args: Namespace) -> None:
    """Execute the `list` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    db_path = get_db_from_invoation(args, args.db)

    if args.list_cultures:
        lines = list_cultures(db_path)

    elif args.list_genders:
        lines = list_genders(db_path)

    elif args.list_kinds:
        lines = list_kinds(db_path)

    else:
        names = db.get_names(db_path)
        if args.culture:
            names = [name for name in names if name.culture == args.culture]
        if args.gender:
            names = [name for name in names if name.gender == args.gender]
        if args.kind:
            names = [name for name in names if name.kind == args.kind]
        lines = list_all_names(names)

    write_output(lines)


def mode_new(args: Namespace) -> None:
    """Execute the `new` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = []

    # Determine the path for the copy.
    path = Path('names.db')
    if args.output:
        path = Path(args.output)
    if path.is_dir():
        path = path / 'names.db'

    # Do not overwrite existing files.
    if path.exists():
        msg = MSGS['en']['new_path_exists'].format(dst_path=path)
        lines.append(msg)

    # Copy the database to the path.
    else:
        db.create_empty_db(path)
        msg = MSGS['en']['new_success'].format(dst_path=path.resolve())
        lines.append(msg)

    # Write any messages to standard out.
    write_output(lines)


# mkname_tools commands.
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


def list_kinds(db_loc: Path) -> tuple[str, ...]:
    """A command script to list the unique kinds in the database.

    :param db_loc: The path to the mkname database.
    :returns: A :class:`tuple` object.
    :rtype: tuple
    """
    return db.get_kinds(db_loc)


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


# Utilities for configuring from invocation.
def get_db_from_invoation(args: Namespace, path: str | Path = '') -> Path:
    """Get the database from the options used when invoking the script."""
    config = load_config(args)
    return load_db_from_config(config, path)


def load_config(args: Namespace) -> Section:
    """Get the config from a config file."""
    config_file = args.config if args.config else ''
    return get_config(config_file)['mkname']


def load_db_from_config(config: Section, path: str | Path = '') -> Path:
    """Get the database based on configuration and invocation."""
    db_path = path if path else config['db_path']
    return Path(get_db(db_path))


# Command parsing.
def parse_cli() -> None:
    """Response to commands passed through the CLI.

    :returns: `None`.
    :rtype: NoneType
    """
    # Set up the command line interface.
    p = ArgumentParser(
        description=(
            'Generate a random name. By default this selects a '
            'random name from the built-in database.'
        ),
        prog='mkname',
    )

    # Name generation modes.
    g_genmodes = p.add_argument_group(
        'Alternate Name Generation Modes',
        description=(
            'Options how the name is generated. The default is to '
            'just select a name from the database.'
        )
    )
    g_exclude = g_genmodes.add_mutually_exclusive_group()
    g_exclude.add_argument(
        '--compound_name', '-c',
        help='Construct a name from two names in the database.',
        action='store_true'
    )
    g_exclude.add_argument(
        '--syllable_name', '-s',
        help=(
            'Construct a name from the syllables of names in the database. '
            'The value of the option is the number of syllables to use.'
        ),
        action='store',
        type=int
    )

    # Post processing.
    g_post = p.add_argument_group(
        'Post Processing',
        description='Options for what happens after a name is generated.'
    )
    g_post.add_argument(
        '--modify_name', '-m',
        help='Modify the name.',
        action='store',
        choices=mods
    )

    # Name selection modification.
    g_filter = p.add_argument_group(
        'Filtering',
        description='Options for filtering data used to generate the name.'
    )
    g_filter.add_argument(
        '--first_name', '-f',
        help='Generate a given name.',
        action='store_true'
    )
    g_filter.add_argument(
        '--gender', '-g',
        help='Generate a name from the given gender.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--last_name', '-l',
        help='Generate a surname.',
        action='store_true'
    )
    g_filter.add_argument(
        '--culture', '-k',
        help='Generate a name from the given culture.',
        action='store',
        type=str
    )

    # Script configuration.
    g_config = p.add_argument_group(
        'Configuration',
        description='Options for configuring the run.'
    )
    g_config.add_argument(
        '--config', '-C',
        help='Use the given custom config file.',
        action='store',
        type=str
    )
    g_config.add_argument(
        '--num_names', '-n',
        help='The number of names to create.',
        action='store',
        type=int,
        default=1
    )

    # Parse the invocation arguments.
    args = p.parse_args()

    # Set up the configuration.
    config = load_config(args)
    db_loc = load_db_from_config(config)

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
        elif args.syllable_name:
            name = build_syllable_name(names, config, args.syllable_name)
            lines.append(name)
        else:
            name = pick_name(names)
            lines.append(name)

    if args.modify_name:
        lines = [modify_name(line, args.modify_name) for line in lines]

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
    p.add_argument(
        '--config', '-f',
        help=(
            'Use the given custom config file. This must be passsed before '
            'the mode.'
        ),
        action='store',
        type=str
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
def parse_add(spa: _SubParsersAction) -> None:
    """Parse the `add` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'add',
        description='Add a name to the database.'
    )
    sp.add_argument(
        'db',
        help='The database to add the data too.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--name', '-n',
        help='The name.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--source', '-s',
        help='The source of the name data.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--culture', '-c',
        help='The culture for the name.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--date', '-d',
        help='The date for the name.',
        action='store',
        type=int
    )
    sp.add_argument(
        '--gender', '-g',
        help='The gender for the name.',
        action='store',
        type=str
    )
    sp.add_argument(
        '--kind', '-k',
        help='The kind for the name.',
        action='store',
        type=str
    )

    sp.set_defaults(func=mode_add)


@subparser('mkname_tools')
def parse_copy(spa: _SubParsersAction) -> None:
    """Parse the `copy` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'copy',
        description='Copy the default names database.'
    )
    sp.add_argument(
        '-o', '--output',
        help='The path to export the data to.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_copy)


@subparser('mkname_tools')
def parse_export(spa: _SubParsersAction) -> None:
    """Parse the `export` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
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
    """Parse the `import` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'import',
        description='Import name data from a file into a names database.'
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
        help='The format of the input file.',
        action='store',
        default='csv',
        choices=INPUT_FORMATS,
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
    sp.add_argument(
        '-u', '--update',
        help='Update names that arleady exist in the database.',
        action='store_true'
    )
    sp.set_defaults(func=mode_import)


@subparser('mkname_tools')
def parse_list(spa: _SubParsersAction) -> None:
    """Parse the `list` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'list',
        description='List data in names databases.'
    )
    sp.add_argument(
        '--db', '-d',
        help='The database to get data from.',
        action='store',
        default='',
        type=str
    )

    # Unique value lists.
    g_values = sp.add_argument_group(
        'List Unique Values',
        description='List the unique values for a specific field.'
    )
    g_exclude = g_values.add_mutually_exclusive_group()
    g_exclude.add_argument(
        '--list_cultures', '-C',
        help='List the cultures.',
        action='store_true'
    )
    g_exclude.add_argument(
        '--list_genders', '-G',
        help='List the genders.',
        action='store_true'
    )
    g_exclude.add_argument(
        '--list_kinds', '-K',
        help='List the kinds.',
        action='store_true'
    )

    # Data filters.
    g_filter = sp.add_argument_group(
        'Data filters',
        description='Filter for the data to be listed.'
    )
    g_filter.add_argument(
        '--culture', '-c',
        help='List names from the given culture.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--gender', '-g',
        help='List names from the given gender.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--kind', '-k',
        help='List names from the given kind.',
        action='store',
        type=str
    )

    sp.set_defaults(func=mode_list)


@subparser('mkname_tools')
def parse_new(spa: _SubParsersAction) -> None:
    """Parse the `new` command for `mkname_tools`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'new',
        description='Create an empty names database.'
    )
    sp.add_argument(
        '-o', '--output',
        help='The path for the empty database.',
        action='store',
        type=str
    )
    sp.set_defaults(func=mode_new)
