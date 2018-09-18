import argparse
import errata_tool.cli.advisory
import errata_tool.cli.build
import errata_tool.cli.product
import errata_tool.cli.release


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
    errata_tool.cli.advisory.add_parser(subparsers)
    errata_tool.cli.build.add_parser(subparsers)
    errata_tool.cli.product.add_parser(subparsers)
    errata_tool.cli.release.add_parser(subparsers)

    args = parser.parse_args()

    if args.stage:
        from errata_tool import ErrataConnector
        ErrataConnector._url = 'https://errata.stage.engineering.redhat.com'

    args.func(args)
