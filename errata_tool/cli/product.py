from errata_tool.product import Product


def add_parser(subparsers):
    """Add our product parser to this top-level subparsers object. """
    group = subparsers.add_parser('product', help='Get a product')

    # product-level subcommands:
    sub = group.add_subparsers(dest='product_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('name', help='eg. "RHCEPH"')
    get_parser.set_defaults(func=get)


def get(args):
    p = Product(name=args.name)
    print('Name: %s' % p.name)
    print('Description: %s' % p.description)
    print('URL: %s' % p.url)
