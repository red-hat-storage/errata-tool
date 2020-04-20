from errata_tool.connector import ErrataConnector


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
    list_parser.set_defaults(func=list_func)


def get_errata_by_batch(connector, batch_name_or_id):
    """search for and return list of errata by name or id of batch"""
    args = {}

    try:
        args['id'] = int(batch_name_or_id)
    except ValueError:
        args['name'] = batch_name_or_id

    data = connector.get_filter('/api/v1/batches', 'filter', **args)

    return data


def get(args):
    et = ErrataConnector()
    e = get_errata_by_batch(et, args.batch_name_or_id)

    # show the raw json returned
    print(e)
    if args.summary:
        print("batch: {0} [{1}]".format(e['data'][0]['attributes']['name'], e['data'][0]['id']))

        print("Release: {0} [{1}]".format(e['data'][0]['relationships']['release']['name'],
            e['data'][0]['relationships']['release']['id']))

        #errata_list = e['data'][0]['relationships']['errata']
        #print(errata_list)
        #errata_id_list = [ i for i in errata_list]
        #print(errata_id_list)
        id_list = [advisory['id'] for advisory in e['data'][0]['relationships']['errata']]
        print("Advisories: " + ",".join([str(entry) for entry in id_list]))



def list_func(args):
    et = ErrataConnector()
    e = et._get('/api/v1/batches')
    print(e)
