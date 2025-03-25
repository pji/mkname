"""
cli
~~~

The :mod:`mkname` package has two command line utilities:
*   `mkname`
*   `mkname_tools`

mkname
======
The `mkname` utility allows you to generate random names at the command
line::

    $ mkname pick
    Barron

The available options and what they do can be found in the help::

    $ mkname -h


mkname_tools
============
The `mkname_tools` utility allows you to perform administrative actions
for `mkname`. For more information, view the help::

    $ mkname_tools -h

"""
import argparse as ap
from collections.abc import Callable, Sequence
from pathlib import Path

from mkname import db
from mkname import mkname as mn
from mkname.constants import MSGS
from mkname.exceptions import *
from mkname.init import get_config, get_db, get_text
from mkname.mod import mods
from mkname.model import Name, Section
from mkname.tools import *


# Constants.
LIST_FIELDS = {
    'cultures': db.get_cultures,
    'dates': db.get_dates,
    'genders': db.get_genders,
    'kinds': db.get_kinds,
    'names': db.get_names,
    'sources': db.get_sources,
}


# Typing.
Subparser = Callable[[ap._SubParsersAction], None]
Registry = dict[str, dict[str, Subparser]]


# Command registration.
subparsers: Registry = {'mkname': {}, 'mkname_tools': {}}


def subparser(script: str) -> Callable[
    [Callable[[ap._SubParsersAction], None]],
    Callable[[ap._SubParsersAction], None]
]:
    def decorator(
        fn: Callable[[ap._SubParsersAction], None]
    ) -> Callable[[ap._SubParsersAction], None]:
        """A decorator for registering subparsers.

        :param fn: The function being registered.
        :return: The registered :class:`collections.abc.Callable`.
        :rtype: collections.abc.Callable
        """
        key = fn.__name__.split('_', 1)[-1]
        subparsers[script][key] = fn
        return fn
    return decorator


# mkname command modes.
def mode_compound(args: ap.Namespace) -> None:
    """Execute the `compound_name` command for `mkname`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = mn.create_compound_name(
        num_names=args.num_names,
        mod=mods[args.modify_name] if args.modify_name else None,
        culture=args.culture,
        date=args.date,
        gender=args.gender,
        kind=args.kind,
        cfg_path=args.config,
        db_path=args.db
    )
    write_output(lines)


def mode_list(args: ap.Namespace) -> None:
    """Execute the `list` command for `mkname`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    if args.field in LIST_FIELDS:
        if args.field == 'names':
            lines = mn.list_names(
                culture=args.culture,
                date=args.date,
                gender=args.gender,
                kind=args.kind,
                cfg_path=args.config,
                db_path=args.db
            )
        else:
            _, db_path = mn.configure(args.config, args.db)
            lines = LIST_FIELDS[args.field](db_path)

    else:
        msg = MSGS['en']['unknown_field'].format(field=args.field)
        lines = [msg,]

    write_output(lines)


def mode_pick(args: ap.Namespace) -> None:
    """Execute the `pick` command for `mkname`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = mn.pick_name(
        num_names=args.num_names,
        mod=mods[args.modify_name] if args.modify_name else None,
        culture=args.culture,
        date=args.date,
        gender=args.gender,
        kind=args.kind,
        cfg_path=args.config,
        db_path=args.db
    )
    write_output(lines)


def mode_syllable(args: ap.Namespace) -> None:
    """Execute the `syllable_name` command for `mkname`.

    :param args: The arguments passed to the script on invocation.
    :returns: `None`.
    :rtype: NoneType
    """
    lines = mn.create_syllable_name(
        num_syllables=args.num_syllables,
        num_names=args.num_names,
        mod=mods[args.modify_name] if args.modify_name else None,
        culture=args.culture,
        date=args.date,
        gender=args.gender,
        kind=args.kind,
        cfg_path=args.config,
        db_path=args.db
    )
    write_output(lines)


# mkname_tools command modes.
def mode_add(args: ap.Namespace) -> None:
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


def mode_copy(args: ap.Namespace) -> None:
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


def mode_export(args: ap.Namespace) -> None:
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


def mode_import(args: ap.Namespace) -> None:
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


def mode_new(args: ap.Namespace) -> None:
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

    p = ap.ArgumentParser(
        description=MSGS['en']['desc_mkname'],
        prog='mkname',
        epilog=get_text('mkname_epilogue.txt'),
        formatter_class=ap.RawDescriptionHelpFormatter
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
    p = ap.ArgumentParser(
        description=MSGS['en']['desc_tools'],
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
    p: ap.ArgumentParser,
    include_num: bool = True
) -> ap.ArgumentParser:
    """Add the configuration arguments for name generation.

    :param p: The :class:`ap.ArgumentParser` to modify.
    :param include_num: (Optional.) Whether to include the
        argument `--num_names`.
    :returns: A :class:`argparse.ap.ArgumentParser` object.
    :rtype: argparse.ap.ArgumentParser
    """
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


def add_filter_args(p: ap.ArgumentParser) -> ap.ArgumentParser:
    """Add the filtering arguments for name generation.

    :param p: The :class:`ap.ArgumentParser` to modify.
    :returns: A :class:`argparse.ap.ArgumentParser` object.
    :rtype: argparse.ap.ArgumentParser
    """
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


def add_postprocessing_args(p: ap.ArgumentParser) -> ap.ArgumentParser:
    """Add the postprocessing arguments for name generation.

    :param p: The :class:`ap.ArgumentParser` to modify.
    :returns: A :class:`argparse.ap.ArgumentParser` object.
    :rtype: argparse.ap.ArgumentParser
    """
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
def parse_compound(spa: ap._SubParsersAction) -> None:
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
    sp.set_defaults(func=mode_compound)


@subparser('mkname')
def parse_pick(spa: ap._SubParsersAction) -> None:
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
def parse_list(spa: ap._SubParsersAction) -> None:
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
def parse_syllable(spa: ap._SubParsersAction) -> None:
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
    sp.set_defaults(func=mode_syllable)


# mkname_tools command subparsing.
@subparser('mkname_tools')
def parse_add(spa: ap._SubParsersAction) -> None:
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
def parse_copy(spa: ap._SubParsersAction) -> None:
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
def parse_export(spa: ap._SubParsersAction) -> None:
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
def parse_import(spa: ap._SubParsersAction) -> None:
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
def parse_new(spa: ap._SubParsersAction) -> None:
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
