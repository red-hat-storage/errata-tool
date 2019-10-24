from errata_tool.build import Build


def add_parser(subparsers):
    """Add build parser to this top-level subparsers object."""
    group = subparsers.add_parser('build', help='Build NVR information')

    # build-level sub-commands:
    sub = group.add_subparsers(dest='build_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('nvr', help='{name}-{version}-{release} of given '
                                        'build')
    get_parser.set_defaults(func=get)


def get(args):
    """Get information about build

    :param args: parsed cli arguments
    """
    build = Build(args.nvr)
    print(build)
