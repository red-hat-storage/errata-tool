from errata_tool.bug import Bug


def add_parser(subparsers):
    """Add build parser to this top-level subparsers object."""
    group = subparsers.add_parser('bug', help='Bugzilla information')

    # build-level sub-commands:
    sub = group.add_subparsers(dest='bug_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('id', help='bugzilla id of given '
                            'bug')
    get_parser.set_defaults(func=get)

    get_all_parser = sub.add_parser('get_errata_ids')
    get_all_parser.add_argument('id', help='bugzilla id of given '
                                'bug')
    get_all_parser.set_defaults(func=get_errata_ids)


def get(args):
    """Get information about bug
    :param args: parsed cli arguments
    """
    bug = Bug(args.id)

    print(bug)
    print(bug._data)


def get_errata_ids(args):
    """Get information about bug
    :param args: parsed cli arguments
    """
    bug = Bug(args.id)
    for id in bug.all_advisory_ids:
        print(id)
