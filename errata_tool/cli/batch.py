from errata_tool.batch import BatchSearch


def add_parser(subparsers):
    """Add our batch parser to this top-level subparsers object. """
    group = subparsers.add_parser('batch', help='Get batch Details')

    # advisory-level subcommands:
    sub = group.add_subparsers(dest='batch_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument(
        'batch_name_or_id', help='batch name or id, "12345" or "<batch name>"')
    get_parser.add_argument('--summary', action='store_true',
                            help="show a bit more details for each advisory"
                            " and list of advisory ids")
    get_parser.set_defaults(func=get)

    # "list"
    list_parser = sub.add_parser('list')

    list_parser.add_argument('--summary', action='store_true',
                             help="show a bit more details for each advisory"
                             " and list of advisory ids")
    list_parser.set_defaults(func=list_func)


def get(args):
    bs = BatchSearch()

    batch_result = bs.search(args.batch_name_or_id)

    # show the raw json returned
    print(batch_result.data)

    if args.summary:
        print(batch_result)


def list_func(args):
    bs = BatchSearch()

    batch_list = bs.list()

    print("Found {0} batches".format(len(batch_list)))
    print(bs._data)

    print(batch_list)

    if args.summary:
        for batch_result in batch_list:
            print(batch_result)
