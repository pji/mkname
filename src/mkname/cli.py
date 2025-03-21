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
from mkname.exceptions import *
from mkname.init import get_config, get_db
from mkname.mod import mods
from mkname.model import Name, Section
from mkname.tools import *


# Constants.
LIST_FIELDS = {
    'cultures': db.get_cultures,
    'genders': db.get_genders,
    'kinds': db.get_kinds,
    'names': db.get_names,
}


# Typing.
Subparser = Callable[[_SubParsersAction], None]
Registry = dict[str, dict[str, Subparser]]


# Command registration.
subparsers: Registry = {'mkname': {}, 'mkname_tools': {}}


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


# Common mkname actions.
def config_mkname(args: Namespace) -> tuple[Section, Path]:
    cfg_path = Path(args.config) if args.config else None
    db_path = Path(args.db) if args.db else None
    config = get_config(cfg_path)['mkname']
    db_loc = get_db(db_path, conf_path=cfg_path)
    return config, db_loc


def filter_mkname(names: Sequence[Name], args: Namespace) -> list[Name]:
    """Filter the names based on the invocation arguments."""
    if args.culture:
        names = [name for name in names if name.culture == args.culture]
    if args.date:
        names = [name for name in names if name.date == args.date]
    if args.gender:
        names = [name for name in names if name.gender == args.gender]
    if args.kind:
        names = [name for name in names if name.kind == args.kind]
    return list(names)


def postprocess_mkname(
    names: Sequence[str],
    args: Namespace
) -> list[str]:
    """Use the given simple mod on the names.

    :param name: The names to modify.
    :param args: The invocation arguments.
    :returns: A :class:`str` object.
    :rtype: str
    """
    if args.modify_name:
        mod = mods[args.modify_name]
        names = [mod(name) for name in names]
    return list(names)


# mkname command modes.
def mode_compound_name(args: Namespace) -> None:
    config, db_loc = config_mkname(args)
    names = db.get_names(db_loc)
    names = filter_mkname(names, args)
    lines = [mn.build_compound_name(
        names,
        config['consonants'],
        config['vowels']
    ) for _ in range(args.num_names)]
    lines = postprocess_mkname(lines, args)
    write_output(lines)


def mode_list(args: Namespace) -> None:
    """Execute the `list` command for `mkname`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    config, db_path = config_mkname(args)

    if args.field in LIST_FIELDS:
        if args.field == 'names':
            names = LIST_FIELDS[args.field](db_path)
            names = filter_mkname(names, args)
            lines = [name.name for name in names]
        else:
            lines = LIST_FIELDS[args.field](db_path)

    else:
        msg = MSGS['en']['unknown_field'].format(field=args.field)
        lines = [msg,]

    write_output(lines)


def mode_pick(args: Namespace) -> None:
    config, db_loc = config_mkname(args)
    names = db.get_names(db_loc)
    names = filter_mkname(names, args)
    lines = [mn.select_name(names) for _ in range(args.num_names)]
    lines = postprocess_mkname(lines, args)
    write_output(lines)


def mode_syllable_name(args: Namespace) -> None:
    config, db_loc = config_mkname(args)
    names = db.get_names(db_loc)
    names = filter_mkname(names, args)
    lines = [mn.build_from_syllables(
        args.num_syllables,
        names,
        config['consonants'],
        config['vowels']
    ) for _ in range(args.num_names)]
    lines = postprocess_mkname(lines, args)
    write_output(lines)


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
    path = Path(args.output) if args.output else None
    try:
        new_path = copy(path)
        msg = MSGS['en']['dup_success'].format(dst_path=new_path.resolve())
    except PathExistsError:
        msg = MSGS['en']['dup_path_exists'].format(dst_path=path)
    lines = (msg,)
    write_output(lines)


def mode_export(args: Namespace) -> None:
    """Execute the `export` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = []
    src_path = args.input if args.input else None
    cfg_path = args.config if args.config else None
    export(dst_path=args.output, src_path=src_path, cfg_path=cfg_path)
    lines.append(MSGS['en']['export_success'].format(path=args.output))
    write_output(lines)


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


def mode_new(args: Namespace) -> None:
    """Execute the `new` command for `mkname_tools`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    path = args.output if args.output else None
    try:
        new_path = new(path)
        msg = MSGS['en']['new_success'].format(dst_path=new_path.resolve())
    except PathExistsError:
        msg = MSGS['en']['new_path_exists'].format(dst_path=path)
    lines = (msg,)
    write_output(lines)


# mkname_tools commands.
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


# Command parsing.
def parse_cli() -> None:
    """Response to commands passed through the CLI.

    :returns: `None`.
    :rtype: NoneType
    """
    subparsers_list = ', '.join(key for key in subparsers['mkname'])

    p = ArgumentParser(
        description=(
            'Generate a random names or read data from a names '
            'database.'
        ),
        prog='mkname',
    )
    spa = p.add_subparsers(
        help=f'Available modes: {subparsers_list}',
        metavar='mode',
        required=True
    )
    for subparser in subparsers['mkname']:
        subparsers['mkname'][subparser](spa)
    args = p.parse_args()
    args.func(args)


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


# Common mkname arguments.
def add_config_args(
    p: ArgumentParser,
    include_num: bool = True
) -> ArgumentParser:
    """Add the configuration arguments for name generation."""
    g_config = p.add_argument_group(
        'Configuration',
        description='Options for configuring the run.'
    )
    g_config.add_argument(
        '--config', '-f',
        help='Use the given custom config file.',
        action='store',
        type=str
    )
    g_config.add_argument(
        '--db', '-d',
        help='Use the given names database.',
        action='store',
        type=str
    )
    if include_num:
        g_config.add_argument(
            '--num_names', '-n',
            help='The number of names to create.',
            action='store',
            type=int,
            default=1
        )
    return p


def add_filter_args(
    p: ArgumentParser,
    include_num: bool = True
) -> ArgumentParser:
    """Add the filtering arguments for name generation."""
    g_filter = p.add_argument_group(
        'Filtering',
        description='Options for filtering data used to generate the name.'
    )
    g_filter.add_argument(
        '--culture', '-c',
        help='Generate a name from the given culture.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--gender', '-g',
        help='Generate a name from the given gender.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--kind', '-k',
        help='Generate a name from the given kind.',
        action='store',
        type=str
    )
    g_filter.add_argument(
        '--date', '-y',
        help='Generate a name from the given date.',
        action='store',
        type=int
    )
    return p


def add_postprocessing_args(
    p: ArgumentParser,
    include_num: bool = True
) -> ArgumentParser:
    """Add the postprocessing arguments for name generation."""
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
    return p


# mkname command subparsing.
@subparser('mkname')
def parse_compound_name(spa: _SubParsersAction) -> None:
    """Parse the `compound_name` command for `mkname`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'compound_name',
        aliases=['compound', 'c'],
        description='Build a compound name from the database.'
    )
    sp = add_config_args(sp)
    sp = add_filter_args(sp)
    sp = add_postprocessing_args(sp)
    sp.set_defaults(func=mode_compound_name)


@subparser('mkname')
def parse_pick(spa: _SubParsersAction) -> None:
    """Parse the `pick` command for `mkname`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'pick',
        aliases=['p',],
        description='Pick a random name from the database.'
    )
    sp = add_config_args(sp)
    sp = add_filter_args(sp)
    sp = add_postprocessing_args(sp)
    sp.set_defaults(func=mode_pick)


@subparser('mkname')
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
        'field',
        help='Which field\'s values to list.',
        action='store',
        choices=LIST_FIELDS,
        type=str
    )
    sp = add_config_args(sp, include_num=False)
    sp = add_filter_args(sp)

    sp.set_defaults(func=mode_list)


@subparser('mkname')
def parse_syllable_name(spa: _SubParsersAction) -> None:
    """Parse the `syllable_name` command for `mkname`.

    :param spa: The subparsers action for `mkname_tools`.
    :returns: `None`.
    :rtype: NoneType
    """
    sp = spa.add_parser(
        'syllable_name',
        aliases=['syllable', 'syl', 's'],
        description='Pick a random name from the database.'
    )
    sp.add_argument(
        'num_syllables',
        help='The number of syllables in the name.',
        action='store',
        type=int
    )
    sp = add_config_args(sp)
    sp = add_filter_args(sp)
    sp = add_postprocessing_args(sp)
    sp.set_defaults(func=mode_syllable_name)


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
        '-i', '--input',
        help='The path to export the data from.',
        action='store',
        type=str
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
