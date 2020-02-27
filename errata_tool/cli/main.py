import argparse
import os
import pkgutil
from importlib import import_module


def import_commands():
    modules = []
    directory = os.path.dirname(__file__)
    for (_, name, _) in pkgutil.iter_modules([directory]):
        if name == 'main':
            continue
        imported_module = import_module('errata_tool.cli.' + name)
        modules.append(imported_module)
    return modules


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', action='store_true',
                        help='use staging ET instance')
    parser.add_argument('--dry-run', action='store_true',
                        help="show what would happen, but don't do it")

    # top-level subcommands:
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    # add arguments for each subcommand:
    commands = import_commands()
    for command in commands:
        command.add_parser(subparsers)

    args = parser.parse_args()

    if args.stage:
        from errata_tool import ErrataConnector
        ErrataConnector._url = 'https://errata.stage.engineering.redhat.com'

    args.func(args)
